# Plot four-stage trajectory and full-track turning-angle dynamics for an example mouse.

import os
from pathlib import Path
from typing import List

import numpy as np
from scipy.io import loadmat

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib_cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
OUT_DIR = SCRIPT_DIR / "data_index"
FIG_DIR = OUT_DIR / "fig1_four_stage_trajectory"

MICE = [
    "dzpm0112201103",  # dzp1
    "dzpm1409201102",  # dzp2
    "dzpm1409201103",  # dzp3
    "vehm0909201102",
    "vehm2206201101",
    "vehm2306201102",
    "vehm2806201101",
    "vehm0212201102",  
]

HOME_RADIUS = 90.0
HOME_X = (HOME_RADIUS * (np.sqrt(2.0) - 1.0)) / np.sqrt(2.0)
HOME = np.array([HOME_X, HOME_X], dtype=float)
ARENA_PADDING = 3.0
VIEW_PADDING = 0.3
VIEW_SCALE = 1.05
LINGER_RATE_THRESHOLD = 0.05


def load_mouse_path(mouse_name: str) -> np.ndarray:
    file_path = DATA_DIR / mouse_name / "data_pos_ling_prog.mat"
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    mat = loadmat(file_path)
    if "data_pos_ling_prog" not in mat:
        raise KeyError(f"data_pos_ling_prog not found in {file_path}")

    data = np.asarray(mat["data_pos_ling_prog"], dtype=float)
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError(f"data_pos_ling_prog must be a 2D array with at least 2 columns: {file_path}")

    path = data[:, :2]
    valid = np.isfinite(path[:, 0]) & np.isfinite(path[:, 1])
    return path[valid]


def translate_first_point_to_home(path: np.ndarray) -> np.ndarray:
    if len(path) == 0:
        return path
    return path + (HOME - path[0])


def split_into_four_stages(path: np.ndarray) -> List[np.ndarray]:
    boundaries = np.linspace(0, len(path), 5, dtype=int)
    return [path[boundaries[i] : boundaries[i + 1]] for i in range(4)]


def remove_lingering_points(path: np.ndarray) -> np.ndarray:
    if len(path) < 2:
        return path[:0]

    dx = np.diff(path[:, 0])
    dy = np.diff(path[:, 1])
    rate = np.hypot(dx, dy)
    keep = np.where(rate >= LINGER_RATE_THRESHOLD)[0]
    return path[keep]


def wrap_to_pi(angle: np.ndarray) -> np.ndarray:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def turning_angle_dynamics(path: np.ndarray) -> np.ndarray:
    if len(path) < 3:
        return np.array([], dtype=float)

    dx = np.diff(path[:, 0])
    dy = np.diff(path[:, 1])
    step_angle = np.arctan2(dy, dx)
    return wrap_to_pi(np.diff(step_angle))


def arena_from_path(path: np.ndarray) -> tuple:
    xmin = float(np.min(path[:, 0]))
    xmax = float(np.max(path[:, 0]))
    ymin = float(np.min(path[:, 1]))
    ymax = float(np.max(path[:, 1]))
    center = np.array([(xmin + xmax) / 2.0, (ymin + ymax) / 2.0], dtype=float)
    radius = max(xmax - xmin, ymax - ymin) / 2.0 + ARENA_PADDING
    return center, radius


def draw_arena(ax: plt.Axes, center: np.ndarray, radius: float) -> None:
    theta = np.linspace(0.0, 2.0 * np.pi, 721)
    ax.plot(
        center[0] + radius * np.cos(theta),
        center[1] + radius * np.sin(theta),
        color="#9a9a9a",
        linewidth=1.5,
    )
    ax.scatter(HOME[0], HOME[1], s=30, color="red", zorder=4)
    view_radius = radius * VIEW_SCALE + VIEW_PADDING
    ax.set_xlim(center[0] - view_radius, center[0] + view_radius)
    ax.set_ylim(center[1] - view_radius, center[1] + view_radius)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()


def plot_turning_angle(ax: plt.Axes, path: np.ndarray) -> np.ndarray:
    turning_angle = turning_angle_dynamics(path)
    x = np.arange(1, len(turning_angle) + 1)
    ax.plot(x, turning_angle, color="black", linewidth=0.1)
    ax.set_ylim(-4.0, 4.0)
    ax.set_yticks([-4.0, 0.0, 4.0])
    ax.set_yticklabels(["-4", "0", "4"])
    ax.set_ylabel(r"$\Delta\theta_t$")
    if len(x):
        ax.set_xlim(float(x[0]), float(x[-1]))
        ax.set_xticks([x[0], x[-1]])
    else:
        ax.set_xticks([0, 1])
    ax.set_xticklabels(["start", "end"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return turning_angle


def plot_four_stage_trajectory(mouse_name: str) -> Path:
    path = translate_first_point_to_home(load_mouse_path(mouse_name))
    stages = split_into_four_stages(path)
    full_no_linger_path = remove_lingering_points(path)
    arena_center, arena_radius = arena_from_path(path)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIG_DIR / f"{mouse_name}_four_stage_trajectory.png"
    svg_path = FIG_DIR / f"{mouse_name}_four_stage_trajectory.svg"
    angle_png_path = FIG_DIR / f"{mouse_name}_turning_angle.png"
    angle_svg_path = FIG_DIR / f"{mouse_name}_turning_angle.svg"
    whole_png_path = FIG_DIR / f"{mouse_name}_whole_trajectory.png"
    whole_svg_path = FIG_DIR / f"{mouse_name}_whole_trajectory.svg"

    fig, axes = plt.subplots(1, 4, figsize=(7.0, 1.22), constrained_layout=False)
    fig.subplots_adjust(left=0.002, right=0.998, top=0.9, bottom=0.002, wspace=0.002)
    titles = ["1st quarter", "2nd quarter", "3rd quarter", "4th quarter"]

    for ax, stage, title in zip(np.ravel(axes), stages, titles):
        draw_arena(ax, arena_center, arena_radius)
        ax.plot(stage[:, 0], stage[:, 1], color="black", linewidth=0.8, alpha=0.9)
        ax.set_aspect("equal", adjustable="box")
        ax.set_axis_off()
        ax.set_title(title, fontsize=10, pad=1.5)

    turning_angle = turning_angle_dynamics(full_no_linger_path)
    std = np.nanstd(turning_angle, ddof=1) if len(turning_angle) > 1 else np.nan
    print(f"{mouse_name} full-track turning angle std (rad): {std:.6g}")

    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(svg_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    angle_fig, angle_ax = plt.subplots(figsize=(2, 1.27), constrained_layout=True)
    plot_turning_angle(angle_ax, full_no_linger_path)
    angle_fig.savefig(angle_png_path, dpi=300)
    angle_fig.savefig(angle_svg_path, dpi=300)
    plt.close(angle_fig)

    whole_fig, whole_ax = plt.subplots(figsize=(2.6, 2.6), constrained_layout=True)
    draw_arena(whole_ax, arena_center, arena_radius)
    whole_ax.plot(path[:, 0], path[:, 1], color="black", linewidth=0.8, alpha=0.9)
    whole_fig.savefig(whole_png_path, dpi=300, bbox_inches="tight")
    whole_fig.savefig(whole_svg_path, dpi=300, bbox_inches="tight")
    plt.close(whole_fig)
    return png_path, svg_path, angle_png_path, angle_svg_path, whole_png_path, whole_svg_path


def main() -> None:
    for mouse_name in MICE:
        (
            png_path,
            svg_path,
            angle_png_path,
            angle_svg_path,
            whole_png_path,
            whole_svg_path,
        ) = plot_four_stage_trajectory(mouse_name)
        print(f"Saved PNG: {png_path}")
        print(f"Saved SVG: {svg_path}")
        print(f"Saved turning angle PNG: {angle_png_path}")
        print(f"Saved turning angle SVG: {angle_svg_path}")
        print(f"Saved whole trajectory PNG: {whole_png_path}")
        print(f"Saved whole trajectory SVG: {whole_svg_path}")


if __name__ == "__main__":
    main()
