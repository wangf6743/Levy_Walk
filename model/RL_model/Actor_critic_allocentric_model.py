#misc
import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import torch 
import numpy as np 
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# for the Actor and Critic neural networks
import torch.nn as nn

RESULTS_DIR = Path("actor_critic_tradeoff_results")





#TASK CONSTANTS
VISITATION_BIN_SIZE =5 # Spatial bin size used to estimate local visitation time, in cm
WEIGHT_HOME = 0.6# Security tradeoff: home vs wall
WEIGHT_TRADEOFF_VALUES = np.round(np.arange(0.0, 1.0001, 0.1), 2) # Reward tradeoff sweep: novelty vs security
HOME_SECURITY_DECAY = 100
WALL_SECURITY_DECAY = 60

# Environment setup
RADIUS = 90  # Wall radius cm
CENTER = np.array([90, 90])
SPEED = 3 # Step length, cm
ACTION_RADIUS = 3 # Number of surrounding bin rings available as actions
ACTION_OFFSETS = np.array([
    [dx, dy]
    for dy in range(ACTION_RADIUS, -ACTION_RADIUS - 1, -1)
    for dx in range(-ACTION_RADIUS, ACTION_RADIUS + 1)
    if dx != 0 or dy != 0
])
ACTION_LABELS = [f"{dx},{dy}" for dx, dy in ACTION_OFFSETS]
STEP_1ST_X = (RADIUS * (np.sqrt(2) - 1) + SPEED) / np.sqrt(2)
STEP_1ST = np.array([STEP_1ST_X, STEP_1ST_X])  # Position at time point 1
HOME_X = (RADIUS * (np.sqrt(2) - 1)) / np.sqrt(2)
HOME = np.array([HOME_X, HOME_X])  # Home / security reference position

#LEARNING CONSTANTS
ETA = 0.01 # Learning rate 
GAMMA = 0.99 #0.99 # Discrete-step discount factor
MAX_SIMULATION_STEPS = 20000 # Maximum number of simulation steps
PRINT_EVERY_STEPS = 1000 # Print training progress every N simulation steps
DEFAULT_TRIALS = 50
DEFAULT_WORKERS = min(len(WEIGHT_TRADEOFF_VALUES) * DEFAULT_TRIALS, os.cpu_count() or 1)
BASE_SEED = 20260720
L2 = 0.000 # L2 regularization
#visualisations



def dist_home(x, home):
    """Calculate Euclidean distance from position x to home"""
    return np.linalg.norm(x - home)


def dist_wall(x, radius, center=CENTER):
    """Calculate distance from position x to the wall (defined by radius)"""
    distance_from_center = np.linalg.norm(x - center)
    return radius - distance_from_center


def sensory_encoding(x, home, radius, visit_count, weight_home, weight_tradeoff=0.5, extent=None):
    """
    Encodes novelty and security information and returns a combined reward.
    
    Args:
        x: Current position (array)
        home: Home position (array)
        radius: Wall radius (scalar)
        visit_count: Number of previous visits to the current spatial bin
        weight_home: Weight for home security vs wall security (0-1)
        weight_tradeoff: Weight between novelty and security (0-1)
    
    Returns:
        reward: Combined novelty-security reward
    """
    # Encoding novelty information
    novelty = np.exp(-visit_count)
    
    # Encoding security information
    dis2home = dist_home(x, home)
    dis2wall = dist_wall(x, radius)
    security_home = np.exp(-dis2home / HOME_SECURITY_DECAY)
    security_wall = np.exp(-dis2wall / WALL_SECURITY_DECAY)
    security = weight_home * security_home + (1 - weight_home) * security_wall
    
    # Combined reward with tradeoff between novelty and security
    reward = weight_tradeoff * novelty + (1 - weight_tradeoff) * security
    
    return reward


def get_sensory_reward(ag, visitation_map, weight_tradeoff=0.3):
    visit_count = visitation_map.observe(ag.pos)
    return sensory_encoding(
        x=ag.pos,
        home=HOME,
        radius=RADIUS,
        visit_count=visit_count,
        weight_home=WEIGHT_HOME,
        weight_tradeoff=weight_tradeoff,
        extent=None,
    )


def generate_free_exploration_env():
    env = CircularFreeExplorationEnvironment(radius=RADIUS, center=CENTER)
    ag = CircularAgent()
    env.add_agent(ag)

    return env, ag




def run_training_step(env,
                      ag,
                      actor,
                      critic,
                      visitation_map,
                      actor_optimizer,
                      critic_optimizer,
                      weight_tradeoff):
    """Run one simulation/training step using the current one-hot bin state."""
    state = visitation_map.state_tensor(ag.pos)
    action_probs = actor(state)
    valid_actions = visitation_map.valid_action_mask(ag.pos, env)
    action, log_prob, action_id = actor.sample_action(
        action_probs,
        valid_actions=valid_actions,
    )


    value = critic(state)
    env.step1(action=action, visitation_map=visitation_map)
    reward = get_sensory_reward(ag, visitation_map, weight_tradeoff)

    next_state = visitation_map.state_tensor(ag.pos)
    with torch.no_grad():
        next_value = critic(next_state)
        td_error = reward + GAMMA * next_value - value.detach()

    critic_optimizer.zero_grad()
    critic_loss = -(value * td_error).sum()
    critic_loss.backward()
    critic_optimizer.step()

    actor_optimizer.zero_grad()
    actor_loss = -(log_prob * td_error).sum()
    actor_loss.backward()
    actor_optimizer.step()

    return reward, action_id


def setup_actor_critic():
    """Create the environment, agent, one-hot state map, actor, and critic."""
    env, ag = generate_free_exploration_env()
    visitation_map = VisitationMap(env)
    n_state = visitation_map.n_bins

    actor = EightNeighborCategoricalMLP(n_in=n_state)
    critic = MultiLayerPerceptron(n_in=n_state)
    actor_optimizer = torch.optim.SGD(actor.parameters(), lr=ETA, weight_decay=L2)
    critic_optimizer = torch.optim.SGD(critic.parameters(), lr=ETA, weight_decay=L2)

    return env, ag, visitation_map, actor, critic, actor_optimizer, critic_optimizer


def train_actor_critic(env,
                       ag,
                       visitation_map,
                       actor,
                       critic,
                       actor_optimizer,
                       critic_optimizer,
                       max_steps=MAX_SIMULATION_STEPS,
                       print_every=PRINT_EVERY_STEPS,
                       weight_tradeoff=0.3):
    """Train actor-critic for the requested number of simulation steps."""
    rewards = []
    actions = []
    try:
        for step in range(max_steps):
            reward, action = run_training_step(
                env,
                ag,
                actor,
                critic,
                visitation_map,
                actor_optimizer,
                critic_optimizer,
                weight_tradeoff,
            )
            rewards.append(reward)
            actions.append(action)
            if print_every and ((step + 1) % print_every == 0 or (step + 1) == max_steps):
                print(f"Simulation step {step + 1}/{max_steps}, reward={reward:.3f}")
    except KeyboardInterrupt:
        print("Interrupted by user")
    print(f"Finished {env.step_count} simulation steps.")
    return rewards, actions


def save_smoothed_trajectory(agent, directory=RESULTS_DIR, smooth=10, step_start=0, step_end=None, trial_index=None):
    """Save the moving-average smoothed trajectory."""
    directory.mkdir(parents=True, exist_ok=True)
    pos = np.array(agent.history["pos"])
    steps = np.array(agent.history["step"])
    if step_end is None:
        step_end = steps[-1]

    mask = (steps >= step_start) & (steps <= step_end)
    selected_steps = steps[mask]
    smoothed_pos = agent._smooth_positions(pos[mask], smooth)
    phase_edges = np.linspace(step_start, step_end, 5)
    phases = np.searchsorted(phase_edges[1:], selected_steps, side="right") + 1
    phases = np.clip(phases, 1, 4)

    csv_data = np.column_stack([
        selected_steps,
        smoothed_pos[:, 0],
        smoothed_pos[:, 1],
        phases,
        np.full(len(selected_steps), smooth, dtype=int),
        np.full(len(selected_steps), -1 if trial_index is None else trial_index, dtype=int),
    ])
    output_path = directory / "smoothed_agent_trajectory.csv"
    np.savetxt(
        output_path,
        csv_data,
        delimiter=",",
        header="step,x_smooth,y_smooth,phase,smooth_window,trial_index",
        comments="",
        fmt=["%d", "%.10f", "%.10f", "%d", "%d", "%d"],
    )
    return output_path


def format_tradeoff_label(weight_tradeoff):
    return f"weight_tradeoff_{weight_tradeoff:.2f}".replace(".", "p")


def phase_for_steps(steps, step_start, step_end):
    phase_edges = np.linspace(step_start, step_end, 5)
    phases = np.searchsorted(phase_edges[1:], steps, side="right") + 1
    return np.clip(phases, 1, 4)


def save_trajectory_history(agent, directory, weight_tradeoff, smooth=10, step_start=0, step_end=None, trial_index=None):
    """Save raw and smoothed positions for one tradeoff run."""
    directory.mkdir(parents=True, exist_ok=True)
    pos = np.array(agent.history["pos"])
    steps = np.array(agent.history["step"])
    if step_end is None:
        step_end = steps[-1]

    mask = (steps >= step_start) & (steps <= step_end)
    selected_steps = steps[mask]
    selected_pos = pos[mask]
    smoothed_pos = agent._smooth_positions(selected_pos, smooth)
    phases = phase_for_steps(selected_steps, step_start, step_end)

    csv_data = np.column_stack([
        selected_steps,
        selected_pos[:, 0],
        selected_pos[:, 1],
        smoothed_pos[:, 0],
        smoothed_pos[:, 1],
        phases,
        np.full(len(selected_steps), smooth, dtype=int),
        np.full(len(selected_steps), weight_tradeoff, dtype=float),
        np.full(len(selected_steps), -1 if trial_index is None else trial_index, dtype=int),
    ])
    output_path = directory / "trajectory.csv"
    np.savetxt(
        output_path,
        csv_data,
        delimiter=",",
        header="step,x,y,x_smooth,y_smooth,phase,smooth_window,weight_tradeoff,trial_index",
        comments="",
        fmt=["%d", "%.10f", "%.10f", "%.10f", "%.10f", "%d", "%d", "%.2f", "%d"],
    )
    return output_path


def critic_value_map(critic, visitation_map):
    """Evaluate critic value for every spatial bin."""
    was_training = critic.training
    critic.eval()
    value_map = np.full((visitation_map.n_x, visitation_map.n_y), np.nan)
    with torch.no_grad():
        for x in range(visitation_map.n_x):
            for y in range(visitation_map.n_y):
                state = np.zeros(visitation_map.n_bins, dtype=np.float32)
                state[x * visitation_map.n_y + y] = 1.0
                state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                value_map[x, y] = critic(state).item()
    if was_training:
        critic.train()
    return value_map


def _draw_arena(ax):
    boundary = plt.Circle(CENTER, radius=RADIUS, fill=False, color="black", linewidth=0.8)
    home_patch = plt.Circle(HOME, radius=RADIUS * 0.03, facecolor="green", alpha=0.2, edgecolor="none")
    ax.add_patch(boundary)
    ax.add_patch(home_patch)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(CENTER[0] - RADIUS - 2, CENTER[0] + RADIUS + 2)
    ax.set_ylim(CENTER[1] - RADIUS - 2, CENTER[1] + RADIUS + 2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save_trajectory_figures(agent, directory, trial_index, weight_tradeoff, smooth=10, step_start=0, step_end=None):
    """Save full and quarter trajectory figures for one trial/tradeoff run."""
    directory.mkdir(parents=True, exist_ok=True)
    pos = np.array(agent.history["pos"])
    steps = np.array(agent.history["step"])
    if step_end is None:
        step_end = steps[-1]

    mask = (steps >= step_start) & (steps <= step_end)
    selected_steps = steps[mask]
    selected_pos = pos[mask]
    plot_pos = agent._smooth_positions(selected_pos, smooth)
    title = "trial {:02d}, weight_tradeoff = {:.2f}".format(trial_index, weight_tradeoff)

    fig, ax = plt.subplots(figsize=(4.2, 4.2), constrained_layout=True)
    _draw_arena(ax)
    ax.plot(plot_pos[:, 0], plot_pos[:, 1], color="black", linewidth=0.35)
    if len(plot_pos):
        ax.scatter(plot_pos[0, 0], plot_pos[0, 1], s=14, color="black", zorder=3)
        ax.scatter(plot_pos[-1, 0], plot_pos[-1, 1], s=14, color="red", zorder=3)
    ax.set_title(title)
    full_png = directory / "trajectory_full.png"
    full_svg = full_png.with_suffix(".svg")
    fig.savefig(full_png, dpi=300, bbox_inches="tight")
    fig.savefig(full_svg, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 4, figsize=(13.2, 3.3), constrained_layout=True)
    phase_edges = np.linspace(step_start, step_end, 5)
    for idx, ax in enumerate(axes):
        phase_mask = (selected_steps >= phase_edges[idx]) & (selected_steps <= phase_edges[idx + 1])
        phase_pos = agent._smooth_positions(selected_pos[phase_mask], smooth)
        _draw_arena(ax)
        if len(phase_pos):
            ax.plot(phase_pos[:, 0], phase_pos[:, 1], color="black", linewidth=0.35)
            ax.scatter(phase_pos[0, 0], phase_pos[0, 1], s=10, color="black", zorder=3)
            ax.scatter(phase_pos[-1, 0], phase_pos[-1, 1], s=10, color="red", zorder=3)
        ax.set_title("Quarter {}".format(idx + 1))
    fig.suptitle(title)
    quarters_png = directory / "trajectory_quarters.png"
    quarters_svg = quarters_png.with_suffix(".svg")
    fig.savefig(quarters_png, dpi=300, bbox_inches="tight")
    fig.savefig(quarters_svg, bbox_inches="tight")
    plt.close(fig)
    return [full_png, full_svg, quarters_png, quarters_svg]


def save_value_distribution(before_values, after_values, visitation_map, directory, weight_tradeoff, trial_index):
    """Save before-learning and after-learning critic values by spatial bin."""
    directory.mkdir(parents=True, exist_ok=True)
    rows = []
    for x in range(visitation_map.n_x):
        for y in range(visitation_map.n_y):
            center = visitation_map.bin_center((x, y))
            inside_circle = 1 if visitation_map.is_valid_bin((x, y), visitation_map.env) else 0
            before = before_values[x, y]
            after = after_values[x, y]
            rows.append([
                trial_index,
                weight_tradeoff,
                x,
                y,
                center[0],
                center[1],
                inside_circle,
                before,
                after,
                after - before,
            ])
    output_path = directory / "value_distribution.csv"
    np.savetxt(
        output_path,
        np.asarray(rows, dtype=float),
        delimiter=",",
        header="trial_index,weight_tradeoff,bin_x,bin_y,center_x,center_y,inside_circle,value_before,value_after,value_delta",
        comments="",
        fmt=["%d", "%.2f", "%d", "%d", "%.10f", "%.10f", "%d", "%.10f", "%.10f", "%.10f"],
    )
    return output_path


def save_reward_history(rewards, directory, weight_tradeoff, trial_index, smooth=100):
    """Save raw rewards and the same moving-average reward trace used for plotting."""
    directory.mkdir(parents=True, exist_ok=True)
    rewards = np.asarray(rewards, dtype=float)
    steps = np.arange(1, len(rewards) + 1, dtype=int)
    if len(rewards) == 0:
        smoothed_rewards = np.asarray([], dtype=float)
    else:
        kernel = np.ones(smooth) / smooth
        smoothed_rewards = np.convolve(rewards, kernel, mode="full")[:len(rewards)]

    csv_data = np.column_stack([
        steps,
        rewards,
        smoothed_rewards,
        np.full(len(rewards), smooth, dtype=int),
        np.full(len(rewards), weight_tradeoff, dtype=float),
        np.full(len(rewards), trial_index, dtype=int),
    ])
    output_path = directory / "reward_history.csv"
    np.savetxt(
        output_path,
        csv_data,
        delimiter=",",
        header="step,reward,reward_smooth,smooth_window,weight_tradeoff,trial_index",
        comments="",
        fmt=["%d", "%.10f", "%.10f", "%d", "%.2f", "%d"],
    )
    return output_path


class VisitationMap:
    """Tracks local visitation counts on a rectangular grid."""

    def __init__(self, env, bin_size=VISITATION_BIN_SIZE):
        self.env = env
        self.extent = env.extent
        self.bin_size = bin_size
        min_x, max_x, min_y, max_y = self.extent
        self.n_x = int(np.ceil((max_x - min_x) / self.bin_size))
        self.n_y = int(np.ceil((max_y - min_y) / self.bin_size))
        self.n_bins = self.n_x * self.n_y
        self.reset()

    def reset(self):
        self.counts = np.zeros((self.n_x, self.n_y), dtype=float)

    def _index(self, pos):
        min_x, max_x, min_y, max_y = self.extent
        x = int(np.clip((pos[0] - min_x) / self.bin_size, 0, self.n_x - 1))
        y = int(np.clip((pos[1] - min_y) / self.bin_size, 0, self.n_y - 1))
        return x, y

    def observe(self, pos):
        idx = self._index(pos)
        visit_count = self.counts[idx]
        self.counts[idx] += 1
        return visit_count

    def flat_index(self, pos):
        x, y = self._index(pos)
        return x * self.n_y + y

    def bin_center(self, idx):
        min_x, max_x, min_y, max_y = self.extent
        x, y = idx
        return np.array([
            min_x + (x + 0.5) * self.bin_size,
            min_y + (y + 0.5) * self.bin_size,
        ])

    def is_valid_bin(self, idx, env):
        x, y = idx
        if x < 0 or x >= self.n_x or y < 0 or y >= self.n_y:
            return False
        return env.is_inside_circle(self.bin_center(idx))

    def valid_action_mask(self, pos, env):
        """Return a boolean mask for actions that keep the agent inside the arena."""
        current_idx = np.array(self._index(pos))
        return np.array([
            self.is_valid_bin(current_idx + offset, env)
            for offset in ACTION_OFFSETS
        ])

    def one_hot_state(self, pos):
        state = np.zeros(self.n_bins, dtype=np.float32)
        state[self.flat_index(pos)] = 1.0
        return state

    def state_tensor(self, pos):
        return torch.tensor(self.one_hot_state(pos), dtype=torch.float32).unsqueeze(0)



class CircularAgent:
    """Minimal agent state/history container for a circular arena."""

    def __init__(self):
        self.pos = STEP_1ST.copy()
        self.prev_pos = HOME.copy()
        self.head_direction = self.pos - self.prev_pos
        self.head_direction = self.head_direction / np.linalg.norm(self.head_direction)
        self.history = {"step": [0], "pos": [self.pos.tolist()], "head_direction": [self.head_direction.tolist()]}

    def save_history(self, step_count):
        self.history["step"].append(step_count)
        self.history["pos"].append(self.pos.tolist())
        self.history["head_direction"].append(self.head_direction.tolist())

    def _smooth_positions(self, positions, smooth):
        if smooth <= 1 or len(positions) < smooth:
            return positions
        kernel = np.ones(smooth) / smooth
        pad_left = smooth // 2
        pad_right = smooth - 1 - pad_left
        padded = np.pad(positions, ((pad_left, pad_right), (0, 0)), mode="edge")
        return np.column_stack([
            np.convolve(padded[:, 0], kernel, mode="valid"),
            np.convolve(padded[:, 1], kernel, mode="valid"),
        ])

class CircularFreeExplorationEnvironment:
    """Circular arena using valid grid-bin actions."""

    def __init__(self, radius=RADIUS, center=CENTER):
        self.radius = radius
        self.center = np.array(center, dtype=float)
        self.extent = np.array([
            self.center[0] - radius,
            self.center[0] + radius,
            self.center[1] - radius,
            self.center[1] + radius,
        ])
        self.step_count = 0
        self.agent = None

    def add_agent(self, agent):
        self.agent = agent

    def is_inside_circle(self, pos):
        return np.linalg.norm(pos - self.center) <= self.radius

    def reset(self):
        self.step_count = 0
        self.agent.pos = STEP_1ST.copy()
        self.agent.prev_pos = HOME.copy()
        self.agent.head_direction = self.agent.pos - self.agent.prev_pos
        self.agent.head_direction = self.agent.head_direction / np.linalg.norm(self.agent.head_direction)
        self.agent.history = {"step": [0], "pos": [self.agent.pos.tolist()], "head_direction": [self.agent.head_direction.tolist()]}
        return self.agent.pos, {}

    def step1(self, action=None, visitation_map=None, *args, **kwargs):
        if visitation_map is None:
            raise ValueError("step1 requires a visitation_map for grid-bin actions.")

        if action is None:
            action = np.random.randint(len(ACTION_OFFSETS))
        current_idx = np.array(visitation_map._index(self.agent.pos))
        target_idx = current_idx + ACTION_OFFSETS[int(action)]
        self.agent.prev_pos = self.agent.pos.copy()
        if visitation_map.is_valid_bin(target_idx, self):
            new_pos = visitation_map.bin_center(target_idx)
            displacement = new_pos - self.agent.pos
            if np.linalg.norm(displacement) > 0:
                self.agent.head_direction = displacement / np.linalg.norm(displacement)
            self.agent.pos = new_pos
        self.step_count += 1
        self.agent.save_history(self.step_count)
        return self.agent.pos, 0, False, False, {}




#=================================== a basic MLP for the CRITIC =======================================
class MultiLayerPerceptron(nn.Module):
    """A generic ReLU neural network class.
    Specify input size, output size and hidden layer sizes (a list). Biases are used by default.

    Args:
        n_in (int, optional): The number of input neurons. Defaults to 20.
        n_out (int, optional): The number of output neurons. Defaults to 1.
        n_hidden (list, optional): A list of integers specifying the number of neurons in each hidden layer. Defaults to [20,20]."""

    def __init__(self, n_in=20, n_out=1, n_hidden=[20,20]):
        nn.Module.__init__(self)
        n = [n_in] + n_hidden + [n_out]
        layers = nn.ModuleList()
        for i in range(len(n)-1):
            layers.append(nn.Linear(n[i],n[i+1]))
            if i < len(n)-2: layers.append(nn.ReLU()) #add a ReLU after each hidden layer (but not the last)
        self.net = nn.Sequential(*layers)

    def forward(self, X):
        """Forward pass, X must be a torch tensor. 
        Returns an (attached) torch tensor through which you can take gradients. """
        return self.net(X)
    

#=================================== a little more wrapping for the ACTOR ===========================================
class EightNeighborCategoricalMLP(MultiLayerPerceptron):
    """Actor network that chooses one of the eight neighboring spatial bins."""
    def __init__(self,n_in, 
                 n_hidden = [50,],
                 n_actions=len(ACTION_OFFSETS)):
        self.n = n_actions
        super().__init__(n_in = n_in, n_hidden=n_hidden, n_out=self.n)
    
    def forward(self, X): #extra softmax layer for probabilities
        return torch.softmax(super().forward(X),dim=1) 
    
    def sample_action(self, firingrate: torch.tensor, valid_actions=None):
        """Sample one neighboring-bin action, optionally masking invalid moves."""
        if valid_actions is not None:
            mask = torch.as_tensor(
                valid_actions,
                dtype=firingrate.dtype,
                device=firingrate.device,
            ).unsqueeze(0)
            masked_firingrate = firingrate * mask
            normalizer = masked_firingrate.sum(dim=1, keepdim=True)
            if torch.any(normalizer <= 0):
                masked_firingrate = firingrate
            else:
                masked_firingrate = masked_firingrate / normalizer
        else:
            masked_firingrate = firingrate

        dist = torch.distributions.Categorical(masked_firingrate)
        choice = dist.sample()
        action = choice.item()
        log_prob = dist.log_prob(choice)
        return action, log_prob, action



def run_tradeoff_experiment(args):
    trial_index, weight_tradeoff, max_steps, print_every, results_dir = args
    torch.set_num_threads(1)
    trial_seed = BASE_SEED + trial_index
    torch.manual_seed(trial_seed)
    np.random.seed(trial_seed)
    label = format_tradeoff_label(weight_tradeoff)
    trial_label = "trial_{:02d}".format(trial_index)
    output_dir = results_dir / trial_label / label
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nRunning {trial_label}/{label}")

    env, ag, visitation_map, actor, critic, actor_optimizer, critic_optimizer = setup_actor_critic()
    value_before = critic_value_map(critic, visitation_map)
    rewards, _actions = train_actor_critic(
        env,
        ag,
        visitation_map,
        actor,
        critic,
        actor_optimizer,
        critic_optimizer,
        max_steps=max_steps,
        print_every=print_every,
        weight_tradeoff=weight_tradeoff,
    )

    value_after = critic_value_map(critic, visitation_map)

    value_path = save_value_distribution(
        value_before,
        value_after,
        visitation_map,
        output_dir,
        weight_tradeoff,
        trial_index,
    )
    reward_path = save_reward_history(rewards, output_dir, weight_tradeoff, trial_index)
    trajectory_path = save_trajectory_history(
        ag,
        output_dir,
        weight_tradeoff,
        smooth=10,
        step_start=0,
        step_end=env.step_count,
        trial_index=trial_index,
    )
    smooth_path = save_smoothed_trajectory(
        ag,
        directory=output_dir,
        smooth=10,
        step_start=0,
        step_end=env.step_count,
        trial_index=trial_index,
    )
    print(f"Saved value distribution: {value_path}")
    print(f"Saved reward history: {reward_path}")
    print(f"Saved trajectory: {trajectory_path}")
    figure_paths = save_trajectory_figures(
        ag,
        output_dir,
        trial_index,
        weight_tradeoff,
        smooth=10,
        step_start=0,
        step_end=env.step_count,
    )
    print(f"Saved smoothed trajectory: {smooth_path}")
    print(f"Saved trajectory figures: {len(figure_paths)} files")

    finite_before = value_before[np.isfinite(value_before)]
    finite_after = value_after[np.isfinite(value_after)]
    reward_arr = np.asarray(rewards, dtype=float)
    return [
        trial_index,
        weight_tradeoff,
        env.step_count,
        float(np.mean(finite_before)) if len(finite_before) else np.nan,
        float(np.mean(finite_after)) if len(finite_after) else np.nan,
        float(np.mean(finite_after - finite_before)) if len(finite_after) else np.nan,
        float(np.mean(reward_arr)) if len(reward_arr) else np.nan,
        float(np.mean(reward_arr[:100])) if len(reward_arr) >= 100 else np.nan,
        float(np.mean(reward_arr[-100:])) if len(reward_arr) >= 100 else np.nan,
    ]


def parse_args():
    parser = argparse.ArgumentParser(description="Run actor-critic tradeoff sweep.")
    parser.add_argument(
        "--trials",
        type=int,
        default=DEFAULT_TRIALS,
        help="number of independent trials per weight_tradeoff",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="parallel worker processes for trial x weight_tradeoff jobs; default uses available CPUs",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=MAX_SIMULATION_STEPS,
        help="training steps per weight_tradeoff",
    )
    parser.add_argument(
        "--print-every",
        type=int,
        default=PRINT_EVERY_STEPS,
        help="progress print interval inside each worker; use 0 to print only final worker output",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RESULTS_DIR,
        help="directory for CSV outputs",
    )
    return parser.parse_args()


def main():
    global MAX_SIMULATION_STEPS
    global PRINT_EVERY_STEPS
    global RESULTS_DIR

    args = parse_args()
    if args.trials < 1:
        raise ValueError("--trials must be at least 1")
    if args.workers < 1:
        raise ValueError("--workers must be at least 1")
    if args.max_steps < 1:
        raise ValueError("--max-steps must be at least 1")
    if args.print_every < 0:
        raise ValueError("--print-every must be non-negative")

    MAX_SIMULATION_STEPS = args.max_steps
    PRINT_EVERY_STEPS = args.print_every
    RESULTS_DIR = args.output_dir
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    tradeoff_values = [float(value) for value in WEIGHT_TRADEOFF_VALUES]
    total_jobs = args.trials * len(tradeoff_values)
    workers = min(args.workers, total_jobs)
    print("Running {} trial(s) x {} tradeoff values = {} jobs with {} worker(s)".format(args.trials, len(tradeoff_values), total_jobs, workers))
    print("Steps per tradeoff: {}".format(MAX_SIMULATION_STEPS))
    print("Output dir: {}".format(RESULTS_DIR))

    worker_args = [
        (trial_index, weight_tradeoff, MAX_SIMULATION_STEPS, PRINT_EVERY_STEPS, RESULTS_DIR)
        for trial_index in range(1, args.trials + 1)
        for weight_tradeoff in tradeoff_values
    ]
    if workers == 1:
        summary_rows = [run_tradeoff_experiment(item) for item in worker_args]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            summary_rows = list(executor.map(run_tradeoff_experiment, worker_args))

    summary_rows = sorted(summary_rows, key=lambda row: (row[0], row[1]))
    summary_path = RESULTS_DIR / "tradeoff_summary.csv"
    np.savetxt(
        summary_path,
        np.asarray(summary_rows, dtype=float),
        delimiter=",",
        header="trial_index,weight_tradeoff,n_steps,value_before_mean,value_after_mean,value_delta_mean,reward_mean,reward_first100_mean,reward_last100_mean",
        comments="",
        fmt=["%d", "%.2f", "%d", "%.10f", "%.10f", "%.10f", "%.10f", "%.10f", "%.10f"],
    )
    print(f"\nSaved tradeoff summary: {summary_path}")


if __name__ == "__main__":
    main()
