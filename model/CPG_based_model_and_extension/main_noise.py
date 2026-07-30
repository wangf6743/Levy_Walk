# This is the extened model with noise. We iterate over the trade-off parameter (alpha),

from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "data_noise"
DEFAULT_NOISE_ETAS = [10.0**exponent for exponent in range(-10, -2, 2)]
DEFAULT_MAX_WORKERS = 8
MAX_RETRY_INITIAL_VALUES = 20


@dataclass
class Track:
    alpha: float
    angle: np.ndarray
    dif_angle: np.ndarray
    location: np.ndarray
    output_cpg: np.ndarray
    output_sc: np.ndarray
    security: np.ndarray
    novelty: np.ndarray
    mental_r: np.ndarray
    occupation: np.ndarray


def f_tent(x: np.ndarray, r: float) -> np.ndarray:
    y = np.empty_like(x, dtype=float)
    below = x < r
    y[below] = x[below] / r
    y[~below] = (1.0 - x[~below]) / (1.0 - r)
    return y


def sigmoid_sc(z: np.ndarray) -> np.ndarray:
    return -1.0 + 2.0 / (1.0 + np.exp(-3.0 * z))


def sigmoid_movement(z: float) -> float:
    return float(-1.0 + 2.0 / (1.0 + np.exp(-9.0 * z)))


def dist_wall(x: np.ndarray, radius: float) -> np.ndarray | float:
    arr = np.asarray(x, dtype=float)
    centered = arr - radius
    distances = radius - np.sqrt(np.sum(centered * centered, axis=-1))
    return float(distances) if distances.ndim == 0 else distances


def dist_home(x: np.ndarray, home: np.ndarray) -> float:
    delta = np.asarray(x, dtype=float) - np.asarray(home, dtype=float)
    return float(np.sqrt(np.sum(delta * delta)))


def sensory_encoding(
    x: np.ndarray,
    home: np.ndarray,
    radius: float,
    vis_time: float,
    weight_home: float,
) -> tuple[float, float]:
    novelty = float(np.exp(-vis_time + 1.0))
    dis2home = dist_home(x, home)
    dis2wall = dist_wall(x, radius)
    security_home = np.exp(-dis2home / 100.0)
    security_wall = np.exp(-dis2wall / 60.0)
    security = weight_home * security_home + (1.0 - weight_home) * security_wall
    return novelty, float(security)


def compute_intersection(
    pres_position: np.ndarray,
    radius: float,
    angle: float,
    speed: float,
) -> np.ndarray:
    step = 0.0001
    num = int(round(speed / step, 1)) + 1
    intervals = np.linspace(0.0, speed, num)
    direction = np.array([np.cos(angle), np.sin(angle)], dtype=float)
    pos_position = pres_position + intervals[:, None] * direction
    dis2wall = np.round(dist_wall(pos_position, radius), 4)
    inside = np.flatnonzero(dis2wall >= 0.0)
    if len(inside) == 0:
        return pos_position[0]
    return pos_position[inside[-1]]


def circle_step3(
    radius: float,
    location: np.ndarray,
    out_location: np.ndarray,
    speed: float,
    out_angle: float,
) -> tuple[np.ndarray, float]:
    center = np.array([radius, radius], dtype=float)
    pre_position = np.round(location, 4)
    pos_position = np.round(out_location, 4)

    intersection = compute_intersection(pre_position, radius, out_angle, speed)
    len_incircle = np.linalg.norm(pre_position - intersection)
    len_outcircle = speed - len_incircle

    original_o2inter = intersection - center
    o2inter = (original_o2inter / np.linalg.norm(original_o2inter)) * radius
    o2pos = pos_position - center
    o2pre = pre_position - center

    trans_angle = len_outcircle / radius
    clock = np.cross(np.array([*o2pre, 0.0]), np.array([*o2pos, 0.0]))
    clock_direction = np.sign(clock[2])
    trans_direction = -1.0 if clock_direction == 0.0 else clock_direction
    trans_vector = trans_direction * trans_angle
    transmatrix = np.array(
        [
            [np.cos(trans_vector), -np.sin(trans_vector)],
            [np.sin(trans_vector), np.cos(trans_vector)],
        ],
        dtype=float,
    )

    o2newloc = transmatrix @ o2inter
    newloc = center + o2newloc

    loc = np.round(newloc - pre_position, 4)
    angle = float(np.arctan2(loc[1], loc[0]))
    return newloc, angle


def gait_generation(
    epsilon1: float,
    epsilon2: float,
    speed: float,
    angle: float,
    location: np.ndarray,
    input_cpg: np.ndarray,
    input_sc: np.ndarray,
    novelty: float,
    security: float,
    weight_novelty: float,
    mental_r: float,
    radius: float,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray, float, float]:
    coupling_cpg = np.array(
        [[1.0 - epsilon1, epsilon1], [epsilon1, 1.0 - epsilon1]],
        dtype=float,
    )
    coupling_sc = np.array(
        [[1.0 - epsilon2, epsilon2], [epsilon2, 1.0 - epsilon2]],
        dtype=float,
    )
    weight_tradeoff = weight_novelty

    output_cpg = coupling_cpg @ f_tent(input_cpg, mental_r)
    output_sc = coupling_sc @ sigmoid_sc(input_sc) + np.array([novelty, security])
    output_mental_r = float(
        0.25 * (weight_tradeoff * output_sc[0] + (1.0 - weight_tradeoff) * output_sc[1])
    )

    dif_angle = float(np.pi * sigmoid_movement(output_cpg[0] - output_cpg[1]))
    out_angle = angle + dif_angle
    out_location = location + speed * np.array([np.cos(out_angle), np.sin(out_angle)])

    if dist_wall(out_location, radius) > 0.0:
        output_location = out_location
        output_angle = out_angle
    else:
        output_location, output_angle = circle_step3(
            radius, location, out_location, speed, out_angle
        )

    return output_angle, output_location, output_cpg, output_sc, dif_angle, output_mental_r



def simulate_control_parameter(
    alpha: float,
    initial_x: float,
    initial_y: float,
    step_number: int,
    noise_eta: float,
    noise_seed: int,
) -> Track:
    rng = np.random.default_rng(noise_seed)
    epsilon1 = 0.218
    input_cpg = np.array([initial_x, initial_y], dtype=float)
    output_cpg_history = np.ones((step_number + 1, 2), dtype=float)
    output_cpg_history[0] = input_cpg

    speed = 0.4
    angle = np.pi * 0.25
    angle_history = np.ones(step_number + 1, dtype=float)
    angle_history[0] = angle
    dif_angle_history = np.ones(step_number, dtype=float)

    weight_novelty = alpha
    weight_security_home = 0.6
    epsilon2 = 0.00001

    input_sc = np.array([1.0, 1.0], dtype=float)
    output_sc_history = np.ones((step_number + 1, 2), dtype=float)
    output_sc_history[0] = input_sc

    novelty = 1.0
    security = 1.0
    mental_r = 0.5 - weight_novelty * 0.5
    novelty_history = np.ones(step_number + 1, dtype=float)
    security_history = np.ones(step_number + 1, dtype=float)
    mental_r_history = np.ones(step_number + 1, dtype=float)
    novelty_history[0] = novelty
    security_history[0] = security
    mental_r_history[0] = mental_r

    radius = 90.0
    step_1st_x = (radius * (np.sqrt(2.0) - 1.0) + speed) / np.sqrt(2.0)
    step_1st = np.array([step_1st_x, step_1st_x], dtype=float)
    home_x = (radius * (np.sqrt(2.0) - 1.0)) / np.sqrt(2.0)
    home = np.array([home_x, home_x], dtype=float)
    location = step_1st.copy()
    location_history = np.ones((step_number + 1, 2), dtype=float)
    location_history[0] = location

    min_x = 0.0
    max_x = radius * 2.0
    min_y = 0.0
    max_y = radius * 2.0
    n_bin_side = 90
    bin_size_x = (max_x - min_x) / n_bin_side
    bin_size_y = (max_y - min_y) / n_bin_side
    occupation = np.zeros((n_bin_side + 1, n_bin_side + 1), dtype=float)
    ind_homex = max(1, int(np.ceil((home[0] - min_x) / bin_size_x)))
    ind_homey = max(1, int(np.ceil((home[1] - min_y) / bin_size_y)))

    for iter_idx in range(1, step_number + 1):
        noisy_input_cpg = input_cpg + rng.normal(0.0, noise_eta, size=2)
        (
            output_angle,
            output_location,
            output_cpg,
            output_sc,
            dif_angle,
            output_mental_r,
        ) = gait_generation(
            epsilon1,
            epsilon2,
            speed,
            angle,
            location,
            noisy_input_cpg,
            input_sc,
            novelty,
            security,
            weight_novelty,
            mental_r,
            radius,
        )

        ind_x = max(1, int(np.ceil((output_location[0] - min_x) / bin_size_x)))
        ind_y = max(1, int(np.ceil((output_location[1] - min_y) / bin_size_y)))
        occupation[ind_x - 1, ind_y - 1] += 1.0
        vis_time = occupation[ind_x - 1, ind_y - 1]
        novelty, security = sensory_encoding(
            output_location,
            home,
            radius,
            vis_time,
            weight_security_home,
        )
        if ind_x == ind_homex and ind_y == ind_homey:
            novelty = 0.0

        angle_history[iter_idx] = output_angle
        angle = output_angle
        dif_angle_history[iter_idx - 1] = dif_angle

        location_history[iter_idx] = output_location
        location = output_location

        output_cpg_history[iter_idx] = output_cpg
        input_cpg = output_cpg

        output_sc_history[iter_idx] = output_sc
        input_sc = output_sc

        novelty_history[iter_idx] = novelty
        security_history[iter_idx] = security

        mental_r_history[iter_idx] = mental_r
        mental_r = output_mental_r

    return Track(
        alpha=float(alpha),
        angle=angle_history,
        dif_angle=dif_angle_history,
        location=location_history,
        output_cpg=output_cpg_history,
        output_sc=output_sc_history,
        security=security_history,
        novelty=novelty_history,
        mental_r=mental_r_history,
        occupation=occupation,
    )


def simulate_control_parameter_with_retries(
    alpha: float,
    initial_x: float,
    initial_y: float,
    step_number: int,
    noise_eta: float,
    noise_seed: int,
    retry_seed: int,
) -> Track:
    retry_rng = np.random.default_rng(retry_seed)
    last_error: Exception | None = None

    for retry_idx in range(MAX_RETRY_INITIAL_VALUES + 1):
        try:
            track = simulate_control_parameter(
                alpha,
                initial_x,
                initial_y,
                step_number,
                noise_eta,
                noise_seed,
            )
            if not np.isfinite(track.location).all():
                raise ValueError("trajectory contains NaN or inf")
            return track
        except (FloatingPointError, OverflowError, ValueError) as error:
            last_error = error
            if retry_idx == MAX_RETRY_INITIAL_VALUES:
                break
            initial_x = float(retry_rng.random())
            initial_y = float(retry_rng.random())
            noise_seed = int(retry_rng.integers(0, np.iinfo(np.uint32).max))

    raise RuntimeError(
        f"Failed alpha={alpha:g}, eta={noise_eta:g} after "
        f"{MAX_RETRY_INITIAL_VALUES} new initial values"
    ) from last_error



def run_simulation(
    trialnumber: int = 50,
    step_number: int = 40000,
    seed: int | None = None,
    workers: int | None = None,
    start_trial: int = 1,
    noise_eta: float = 0.0,
) -> list[list[Track]]:
    rng = np.random.default_rng(seed)
    trackdata: list[list[Track]] = []
    alpha_values = [round(idx * 0.1, 1) for idx in range(11)]
    requested_workers = workers if workers is not None else DEFAULT_MAX_WORKERS
    max_workers = min(requested_workers, DEFAULT_MAX_WORKERS, len(alpha_values), os.cpu_count() or 1)

    for trial_idx in range(trialnumber):
        current_trial = start_trial + trial_idx
        print(f"Running Trial {current_trial}/{start_trial + trialnumber - 1}")
        initial_x = rng.random()
        initial_y = rng.random()
        noise_seeds = rng.integers(
            0,
            np.iinfo(np.uint32).max,
            size=len(alpha_values),
            dtype=np.uint32,
        ).astype(int)
        retry_seeds = rng.integers(
            0,
            np.iinfo(np.uint32).max,
            size=len(alpha_values),
            dtype=np.uint32,
        ).astype(int)

        if max_workers == 1:
            trial_tracks = [
                simulate_control_parameter_with_retries(
                    alpha,
                    initial_x,
                    initial_y,
                    step_number,
                    noise_eta,
                    int(noise_seed),
                    int(retry_seed),
                )
                for alpha, noise_seed, retry_seed in zip(alpha_values, noise_seeds, retry_seeds)
            ]
        else:
            print(f"  Running {len(alpha_values)} alpha values with {max_workers} workers")
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                trial_tracks = list(
                    executor.map(
                        simulate_control_parameter_with_retries,
                        alpha_values,
                        [initial_x] * len(alpha_values),
                        [initial_y] * len(alpha_values),
                        [step_number] * len(alpha_values),
                        [noise_eta] * len(alpha_values),
                        noise_seeds,
                        retry_seeds,
                    )
                )

        trackdata.append(trial_tracks)

    return trackdata

def run_trial_noise_alpha_grid(
    trialnumber: int = 50,
    step_number: int = 40000,
    seed: int | None = None,
    workers: int | None = None,
    start_trial: int = 1,
    noise_etas: list[float] | None = None,
) -> list[tuple[int, float, list[Track]]]:
    rng = np.random.default_rng(seed)
    alpha_values = [round(idx * 0.1, 1) for idx in range(11)]
    eta_values = list(DEFAULT_NOISE_ETAS if noise_etas is None else noise_etas)
    requested_workers = workers if workers is not None else DEFAULT_MAX_WORKERS
    max_workers = min(requested_workers, DEFAULT_MAX_WORKERS, len(alpha_values), os.cpu_count() or 1)
    results: list[tuple[int, float, list[Track]]] = []

    for trial_idx in range(trialnumber):
        current_trial = start_trial + trial_idx
        print(f"Running Trial {current_trial}/{start_trial + trialnumber - 1}")
        initial_x = rng.random()
        initial_y = rng.random()

        for noise_eta in eta_values:
            print(f"  Running eta={noise_eta:g} across {len(alpha_values)} alpha values")
            noise_seeds = rng.integers(
                0,
                np.iinfo(np.uint32).max,
                size=len(alpha_values),
                dtype=np.uint32,
            ).astype(int)
            retry_seeds = rng.integers(
                0,
                np.iinfo(np.uint32).max,
                size=len(alpha_values),
                dtype=np.uint32,
            ).astype(int)

            if max_workers == 1:
                trial_tracks = [
                    simulate_control_parameter_with_retries(
                        alpha,
                        initial_x,
                        initial_y,
                        step_number,
                        noise_eta,
                        int(noise_seed),
                        int(retry_seed),
                    )
                    for alpha, noise_seed, retry_seed in zip(alpha_values, noise_seeds, retry_seeds)
                ]
            else:
                with ProcessPoolExecutor(max_workers=max_workers) as executor:
                    trial_tracks = list(
                        executor.map(
                            simulate_control_parameter_with_retries,
                            alpha_values,
                            [initial_x] * len(alpha_values),
                            [initial_y] * len(alpha_values),
                            [step_number] * len(alpha_values),
                            [noise_eta] * len(alpha_values),
                            noise_seeds,
                            retry_seeds,
                        )
                    )

            results.append((current_trial, float(noise_eta), trial_tracks))

    return results


def format_alpha_filename(alpha: float) -> str:
    alpha_text = f"{alpha:g}".replace("-", "minus_").replace(".", "p")
    return f"alpha_{alpha_text}.csv"


def format_eta_dirname(eta: float) -> str:
    eta_text = f"{eta:.0e}".replace("e-", "e_minus_").replace("e+", "e")
    return f"eta_{eta_text}"


def save_csv_files(trackdata: list[list[Track]], output_dir: Path, start_trial: int = 1) -> None:
    for trial_idx, trial_tracks in enumerate(trackdata, start=start_trial):
        trial_dir = output_dir / f"trial_{trial_idx:02d}"
        trial_dir.mkdir(parents=True, exist_ok=True)

        for control_idx, track in enumerate(trial_tracks, start=1):
            dif_angle = np.empty_like(track.angle)
            dif_angle[0] = np.nan
            dif_angle[1:] = track.dif_angle

            csv_data = np.column_stack(
                [
                    np.arange(len(track.angle), dtype=int),
                    track.location[:, 0],
                    track.location[:, 1],
                    track.angle,
                    dif_angle,
                    track.output_cpg[:, 0],
                    track.output_cpg[:, 1],
                    track.output_sc[:, 0],
                    track.output_sc[:, 1],
                    track.security,
                    track.novelty,
                    track.mental_r,
                ]
            )
            output_path = trial_dir / format_alpha_filename(track.alpha)
            np.savetxt(
                output_path,
                csv_data,
                delimiter=",",
                header=(
                    "step,x,y,angle,dif_angle,"
                    "output_cpg_1,output_cpg_2,output_sc_1,output_sc_2,"
                    "security,novelty,mental_r"
                ),
                comments="",
            )


def save_noise_alpha_grid_csv_files(results: list[tuple[int, float, list[Track]]], output_dir: Path) -> None:
    for trial_idx, noise_eta, trial_tracks in results:
        eta_dir = output_dir / f"trial_{trial_idx:02d}" / format_eta_dirname(noise_eta)
        eta_dir.mkdir(parents=True, exist_ok=True)

        for track in trial_tracks:
            dif_angle = np.empty_like(track.angle)
            dif_angle[0] = np.nan
            dif_angle[1:] = track.dif_angle

            csv_data = np.column_stack(
                [
                    np.arange(len(track.angle), dtype=int),
                    track.location[:, 0],
                    track.location[:, 1],
                    track.angle,
                    dif_angle,
                    track.output_cpg[:, 0],
                    track.output_cpg[:, 1],
                    track.output_sc[:, 0],
                    track.output_sc[:, 1],
                    track.security,
                    track.novelty,
                    track.mental_r,
                    np.full(len(track.angle), noise_eta, dtype=float),
                ]
            )
            output_path = eta_dir / format_alpha_filename(track.alpha)
            np.savetxt(
                output_path,
                csv_data,
                delimiter=",",
                header=(
                    "step,x,y,angle,dif_angle,"
                    "output_cpg_1,output_cpg_2,output_sc_1,output_sc_2,"
                    "security,novelty,mental_r,noise_eta"
                ),
                comments="",
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python version of model/main.m")
    parser.add_argument("--trials", type=int, default=50, help="number of trials")
    parser.add_argument("--start-trial", type=int, default=1, help="starting trial index for output folders")
    parser.add_argument("--steps", type=int, default=40_000, help="steps per alpha value")
    parser.add_argument("--seed", type=int, default=None, help="random seed")
    parser.add_argument(
        "--etas",
        type=float,
        nargs="+",
        default=DEFAULT_NOISE_ETAS,
        help="noise sigma values; defaults to 1e-10 1e-8 1e-6 1e-4",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="parallel workers for alpha values within each trial; default uses up to 8 CPUs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory for saving trial folders and alpha CSV files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    total_start = time.perf_counter()

    print(f"Noise etas: {[float(eta) for eta in args.etas]}")
    results = run_trial_noise_alpha_grid(
        trialnumber=args.trials,
        step_number=args.steps,
        seed=args.seed,
        workers=args.workers,
        start_trial=args.start_trial,
        noise_etas=args.etas,
    )
    save_noise_alpha_grid_csv_files(results, args.output_dir)

    elapsed = time.perf_counter() - total_start
    print(f"running time:{elapsed}")
    print(f"saved data:{args.output_dir}")


if __name__ == "__main__":
    main()
