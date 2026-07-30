# this code is for the  analysis for the
# dynamics of the behavioral metrics for all the mice
# mianly about the temporal differerences for all animals .

from __future__ import annotations

import csv
import os
from pathlib import Path
import time

import numpy as np
from scipy.io import loadmat, savemat
from scipy.stats import f_oneway

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib_cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
})


# =========================
# Paths
# =========================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
OUT_DIR = SCRIPT_DIR / "data_index"
CSV_DIR = SCRIPT_DIR / "behabiral_metrices_all"
FIG_DIR = OUT_DIR / "workflow_metric_figs"

PER_MOUSE_CSV = CSV_DIR / "workflow_metrics_full_and_quarters.csv"
GROUP_SUMMARY_CSV = CSV_DIR / "workflow_metrics_group_summary.csv"
ANOVA_CSV = CSV_DIR / "workflow_metrics_group_anova.csv"
PATHLET_CSV = CSV_DIR / "workflow_metrics_full_track_100step_pathlets.csv"
PATHLET_GROUP_SUMMARY_CSV = CSV_DIR / "workflow_metrics_full_track_100step_pathlet_group_summary.csv"
PATHLET_ANOVA_CSV = CSV_DIR / "workflow_metrics_full_track_100step_pathlet_anova.csv"
PATHLET_FILTER_SUMMARY_CSV = CSV_DIR / "workflow_metrics_full_track_100step_pathlet_filter_summary.csv"
PATHLET_FIG_DIR = CSV_DIR / "metric_plots_pathlets"
MAT_PATH = OUT_DIR / "workflow_metrics_full_and_quarters.mat"
QUARTER_PATHLET_CSV = CSV_DIR / "workflow_metrics_quarter_pathlets_across_mice.csv"
QUARTER_SUMMARY_CSV = CSV_DIR / "workflow_metrics_quarter_pathlets_across_mice_summary.csv"
QUARTER_ANOVA_CSV = CSV_DIR / "workflow_metrics_quarter_pathlets_time_effect_anova.csv"
QUARTER_FIG_DIR = CSV_DIR / "metric_plots_quarter_pathlets_across_mice"


# =========================
# Mice
# =========================
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


# =========================
# Parameters
# =========================
N_BIN_SIDE = 90
ARENA_MASK_RADIUS_SCALE = 1.05
LINGER_RATE_THRESHOLD = 0.05 # speed: 0.05cm/0.04s
PATHLET_STEP_LENGTH = 100
WALL_MARGIN = 5.0

# Only calculate the filtered version for the pathlet analysis.
DELETE_LINGERING_OPTIONS = [True]
REMOVE_WALL_OPTIONS = [False]

STAGE_NAMES = ["quarter_1", "quarter_2", "quarter_3", "quarter_4"]
QUARTER_LABELS = ["1st quarter", "2nd quarter", "3rd quarter", "4th quarter"]
METRIC_NAMES = ["msd", "spatial_coverage", "exploration_entropy", "sda", "mean_speed"]
PATHLET_METRIC_NAMES = ["msd", "spatial_coverage", "exploration_entropy", "sda", "mean_speed"]
PATHLET_STAGE_NAMES = ["full", "last_3_quarters"]

METRIC_LABELS = {
    "mean_speed": "Mean speed (cm/s)",
    "msd": "Dispersal (cm$^2$)",
    "sda": r"S.D. of $\Delta\theta_t$",
    "spatial_coverage": "Spatial coverage (%)",
    "exploration_entropy": "Exploration entropy",
}

GROUP_COLORS = {
    "DZP": "#0072B2",
    "VEH": "#D55E00",
}




# =========================
# Basic utilities
# =========================
def group_for_mouse(mouse_name: str) -> str:
    lower_name = mouse_name.lower()
    if lower_name.startswith("dzp"):
        return "DZP"
    if lower_name.startswith("veh"):
        return "VEH"
    return "UNKNOWN"


def load_track(mouse_name: str) -> np.ndarray:
    file_path = DATA_DIR / mouse_name / "data_pos_ling_prog.mat"
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    mat = loadmat(file_path)
    if "data_pos_ling_prog" not in mat:
        raise KeyError(f"data_pos_ling_prog not found in {file_path}")

    track = np.asarray(mat["data_pos_ling_prog"], dtype=float)
    if track.ndim != 2 or track.shape[1] < 2:
        raise ValueError(f"data_pos_ling_prog must be a 2D array with at least 2 columns: {file_path}")

    track = track[:, :2]
    track = track[np.all(np.isfinite(track), axis=1)]
    return track


def comput_traject_polar(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Python version of MATLAB comput_traject_polar."""
    dx = np.diff(x)
    dy = np.diff(y)
    rate = np.hypot(dx, dy)
    angle = np.arctan2(dy, dx)
    return rate, angle


def mouse_wall_geometry(path: np.ndarray) -> tuple[np.ndarray, float]:
    center = np.array(
        [
            0.5 * (np.nanmax(path[:, 0]) + np.nanmin(path[:, 0])),
            0.5 * (np.nanmax(path[:, 1]) + np.nanmin(path[:, 1])),
        ],
        dtype=float,
    )
    home = path[0, :2]
    radius = float(np.linalg.norm(center - home))
    return center, radius


def remove_near_wall_points(
    path: np.ndarray,
    center: np.ndarray,
    radius: float,
    wall_margin: float = WALL_MARGIN,
) -> np.ndarray:
    if len(path) == 0:
        return path.copy()

    inner_radius = max(radius - wall_margin, 0.0)
    distance_from_center = np.linalg.norm(path[:, :2] - center, axis=1)
    return path[distance_from_center < inner_radius, :]


def remove_lingering(path: np.ndarray, threshold: float = LINGER_RATE_THRESHOLD) -> np.ndarray:
    """
    Remove lingering samples using rate >= threshold.

    This follows the MATLAB-like logic in the workflow:
        [rate, Angle] = comput_traject_polar(path(:,1), path(:,2));
        ind = find(rate >= 0.05);
        path = path(ind,:);

    Note: rate has length len(path)-1, so this keeps the starting point of each valid step.
    """
    if len(path) < 2:
        return path.copy()

    rate, _angle = comput_traject_polar(path[:, 0], path[:, 1])
    keep_indices = np.where(rate >= threshold)[0]
    return path[keep_indices, :]


def split_full_and_quarters(path: np.ndarray) -> dict[str, np.ndarray]:
    """Return full path and four equal-length periods."""
    n = len(path)
    q1 = n // 4
    q2 = n // 2
    q3 = (3 * n) // 4
    return {
        "full": path,
        "period_1": path[:q1],
        "period_2": path[q1:q2],
        "period_3": path[q2:q3],
        "period_4": path[q3:n],
    }


def split_full_and_quarters_after_lingering(path: np.ndarray, threshold: float = LINGER_RATE_THRESHOLD) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Split the full path into stages, then remove lingering samples using full-path speed."""
    n = len(path)
    q1 = n // 4
    q2 = n // 2
    q3 = (3 * n) // 4
    bounds = {
        "full": (0, n),
        "period_1": (0, q1),
        "period_2": (q1, q2),
        "period_3": (q2, q3),
        "period_4": (q3, n),
    }
    speed = compute_step_speed(path)
    speed_threshold = threshold / FRAME_INTERVAL_SECONDS
    stages: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for stage, (start, stop) in bounds.items():
        if stop - start < 2 or len(speed) == 0:
            stages[stage] = (path[start:stop].copy(), np.asarray([], dtype=float))
            continue
        step_start = min(start, len(speed))
        step_stop = min(stop - 1, len(speed))
        keep_steps = np.where(speed[step_start:step_stop] >= speed_threshold)[0] + step_start
        stages[stage] = (path[keep_steps, :], speed[keep_steps])
    return stages


def build_arena(all_tracks: dict[str, np.ndarray]) -> dict[str, np.ndarray | float]:
    """
    Build a common circular arena from all mice.

    Spatial coverage denominator uses circular-field bins, not the whole square.
    The circle is defined from the global x/y range: center is the middle of the
    global bounding box; radius is half of the shorter side.
    """
    all_points = np.vstack([track for track in all_tracks.values() if len(track) > 0])
    min_x = float(np.nanmin(all_points[:, 0]))
    max_x = float(np.nanmax(all_points[:, 0]))
    min_y = float(np.nanmin(all_points[:, 1]))
    max_y = float(np.nanmax(all_points[:, 1]))

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    radius = (min(max_x - min_x, max_y - min_y) / 2.0) * ARENA_MASK_RADIUS_SCALE

    # Use exactly N_BIN_SIDE x N_BIN_SIDE bins. The workflow note used
    # occupation = zeros(n_bin_side + 1, n_bin_side + 1); for Python indexing,
    # fixed N_BIN_SIDE bins are simpler and avoid edge overflow.
    x_edges = np.linspace(min_x, max_x, N_BIN_SIDE + 1)
    y_edges = np.linspace(min_y, max_y, N_BIN_SIDE + 1)
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2.0
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2.0
    xx, yy = np.meshgrid(x_centers, y_centers, indexing="ij")
    circular_bin_mask = (xx - center_x) ** 2 + (yy - center_y) ** 2 <= radius**2

    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "center_x": center_x,
        "center_y": center_y,
        "radius": radius,
        "x_edges": x_edges,
        "y_edges": y_edges,
        "circular_bin_mask": circular_bin_mask,
    }


def bin_indices(path: np.ndarray, arena: dict[str, np.ndarray | float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Map x/y samples to bin indices and return only samples inside the circular arena."""
    if len(path) == 0:
        empty = np.array([], dtype=int)
        return empty, empty, np.array([], dtype=bool)

    x_edges = np.asarray(arena["x_edges"], dtype=float)
    y_edges = np.asarray(arena["y_edges"], dtype=float)
    circular_bin_mask = np.asarray(arena["circular_bin_mask"], dtype=bool)

    ix = np.searchsorted(x_edges, path[:, 0], side="right") - 1
    iy = np.searchsorted(y_edges, path[:, 1], side="right") - 1

    # Include samples exactly at the max edge.
    ix = np.clip(ix, 0, N_BIN_SIDE - 1)
    iy = np.clip(iy, 0, N_BIN_SIDE - 1)

    inside_circle = circular_bin_mask[ix, iy]
    return ix[inside_circle], iy[inside_circle], inside_circle


# =========================
# Metrics
# =========================
def compute_msd(path: np.ndarray) -> float:
    """
    Mean squared displacement relative to the first sample of this path/stage.

    This is the mean of squared distance from the starting point:
        mean((x_t - x_0)^2 + (y_t - y_0)^2)
    """
    if len(path) < 2:
        return np.nan
    displacement = path - path[0, :]
    squared_distance = displacement[:, 0] ** 2 + displacement[:, 1] ** 2
    return float(np.nanmean(squared_distance))


def compute_occupancy_counts(path: np.ndarray, arena: dict[str, np.ndarray | float]) -> np.ndarray:
    """Count visits to spatial bins. Consecutive stays in the same bin are counted repeatedly."""
    counts = np.zeros((N_BIN_SIDE, N_BIN_SIDE), dtype=float)
    ix, iy, _inside = bin_indices(path, arena)
    if len(ix) == 0:
        return counts
    np.add.at(counts, (ix, iy), 1.0)
    return counts


def compute_spatial_coverage(path: np.ndarray, arena: dict[str, np.ndarray | float]) -> float:
    """Visited circular bins divided by all circular-field bins."""
    circular_bin_mask = np.asarray(arena["circular_bin_mask"], dtype=bool)
    n_circular_bins = int(np.sum(circular_bin_mask))
    if n_circular_bins == 0 or len(path) == 0:
        return np.nan

    counts = compute_occupancy_counts(path, arena)
    visited_circular_bins = (counts > 0) & circular_bin_mask
    return float(100.0 * np.sum(visited_circular_bins) / n_circular_bins)


def compute_exploration_entropy(path: np.ndarray, arena: dict[str, np.ndarray | float]) -> float:
    """
    Cumulative occupancy entropy over spatial bins.

    O_i = C_i / sum_j C_j
    E = -sum_i O_i * log2(O_i)
    """
    circular_bin_mask = np.asarray(arena["circular_bin_mask"], dtype=bool)
    n_circular_bins = int(np.sum(circular_bin_mask))
    if n_circular_bins <= 1 or len(path) == 0:
        return np.nan

    counts = compute_occupancy_counts(path, arena)
    circular_counts = counts[circular_bin_mask]
    total_counts = float(np.sum(circular_counts))
    if total_counts <= 0:
        return np.nan

    prob = circular_counts / total_counts
    prob = prob[prob > 0]
    return float(-np.sum(prob * np.log2(prob)))


def wrap_to_pi(angle: np.ndarray) -> np.ndarray:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def compute_sda(path: np.ndarray) -> float:
    """
    Standard deviation of relative turning angle.

    Equivalent to the workflow logic:
      1. compute angle of each step
      2. rotate next step into the current-step reference frame
      3. get relative angle by atan2
      4. std(relative angles)
    """
    if len(path) < 3:
        return np.nan

    x = path[:, 0]
    y = path[:, 1]
    _rate, angle = comput_traject_polar(x, y)
    if len(angle) < 2:
        return np.nan

    relative_angle = wrap_to_pi(angle[1:] - angle[:-1])
    if len(relative_angle) == 0:
        return np.nan
    return float(np.nanstd(relative_angle, ddof=1)) if len(relative_angle) > 1 else 0.0


FRAME_INTERVAL_SECONDS = 0.04


def compute_step_speed(path: np.ndarray) -> np.ndarray:
    """Step speed in cm/s, computed from consecutive path samples."""
    if len(path) < 2:
        return np.asarray([], dtype=float)
    rate, _angle = comput_traject_polar(path[:, 0], path[:, 1])
    return np.asarray(rate, dtype=float) / FRAME_INTERVAL_SECONDS


def compute_speed_stats(speed: np.ndarray) -> float:
    """Mean speed in cm/s from precomputed full-track speed values."""
    rate = np.asarray(speed, dtype=float)
    rate = rate[np.isfinite(rate)]
    if len(rate) == 0:
        return np.nan
    return float(np.nanmean(rate))


def compute_all_metrics(path: np.ndarray, arena: dict[str, np.ndarray | float], speed: np.ndarray | None = None) -> dict[str, float]:
    cumulative_entropy = compute_exploration_entropy(path, arena)
    mean_speed = compute_speed_stats(compute_step_speed(path) if speed is None else speed)
    return {
        "msd": compute_msd(path),
        "spatial_coverage": compute_spatial_coverage(path, arena),
        "exploration_entropy": cumulative_entropy,
        "sda": compute_sda(path),
        "mean_speed": mean_speed,
    }


def compute_pathlet_metrics(pathlet: np.ndarray, arena: dict[str, np.ndarray | float], speed: np.ndarray | None = None) -> dict[str, float]:
    cumulative_entropy = compute_exploration_entropy(pathlet, arena)
    mean_speed = compute_speed_stats(compute_step_speed(pathlet) if speed is None else speed)
    return {
        "msd": compute_msd(pathlet),
        "spatial_coverage": compute_spatial_coverage(pathlet, arena),
        "exploration_entropy": cumulative_entropy,
        "sda": compute_sda(pathlet),
        "mean_speed": mean_speed,
    }


def pathlet_stage_paths(path: np.ndarray) -> dict[str, np.ndarray]:
    """Return full path and the last 3/4 of the same path."""
    return {
        "full": path,
        "last_3_quarters": path[len(path) // 4:],
    }


def pathlet_stage_paths_with_speed(path: np.ndarray, speed: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Return full and last-3-quarters pathlets with matching precomputed speed values."""
    start = len(path) // 4
    return {
        "full": (path, speed),
        "last_3_quarters": (path[start:], speed[start:]),
    }


def iter_full_track_pathlets(path: np.ndarray) -> list[tuple[int, np.ndarray]]:
    n_pathlets = len(path) // PATHLET_STEP_LENGTH
    return [
        (pathlet_index + 1, path[pathlet_index * PATHLET_STEP_LENGTH:(pathlet_index + 1) * PATHLET_STEP_LENGTH])
        for pathlet_index in range(n_pathlets)
    ]


def iter_full_track_pathlets_with_speed(path: np.ndarray, speed: np.ndarray) -> list[tuple[int, np.ndarray, np.ndarray]]:
    n_pathlets = len(path) // PATHLET_STEP_LENGTH
    return [
        (
            pathlet_index + 1,
            path[pathlet_index * PATHLET_STEP_LENGTH:(pathlet_index + 1) * PATHLET_STEP_LENGTH],
            speed[pathlet_index * PATHLET_STEP_LENGTH:(pathlet_index + 1) * PATHLET_STEP_LENGTH],
        )
        for pathlet_index in range(n_pathlets)
    ]


# =========================
# Output helpers
# =========================
def write_per_mouse_csv(rows: list[dict[str, object]]) -> None:
    with PER_MOUSE_CSV.open("w", newline="") as f:
        fieldnames = [
            "mouse",
            "group",
            "delete_lingering",
            "stage",
            *METRIC_NAMES,
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_pathlet_csv(rows: list[dict[str, object]]) -> None:
    with PATHLET_CSV.open("w", newline="") as f:
        fieldnames = [
            "mouse",
            "group",
            "delete_lingering",
            "remove_wall",
            "wall_margin",
            "stage",
            "pathlet_index",
            *PATHLET_METRIC_NAMES,
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_pathlet_filter_summary(rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "mouse",
        "group",
        "delete_lingering",
        "remove_wall",
        "wall_margin",
        "n_raw_points",
        "n_after_lingering",
        "n_after_wall",
        "n_lingering_removed",
        "n_wall_removed",
        "wall_center_x",
        "wall_center_y",
        "wall_radius",
    ]
    with PATHLET_FILTER_SUMMARY_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def finite_values(rows: list[dict[str, object]], group: str, stage: str, delete_lingering: bool, metric: str) -> np.ndarray:
    values = np.asarray(
        [
            float(row[metric])
            for row in rows
            if row["group"] == group and row["stage"] == stage and row["delete_lingering"] == delete_lingering
        ],
        dtype=float,
    )
    return values[np.isfinite(values)]


def write_group_summary(rows: list[dict[str, object]]) -> None:
    with GROUP_SUMMARY_CSV.open("w", newline="") as f:
        fieldnames = ["metric", "stage", "delete_lingering", "group", "n_mice", "mean", "std", "sem"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for delete_lingering in DELETE_LINGERING_OPTIONS:
            for stage in STAGE_NAMES:
                for metric in METRIC_NAMES:
                    for group in ["DZP", "VEH"]:
                        values = finite_values(rows, group, stage, delete_lingering, metric)
                        n = len(values)
                        std = float(np.nanstd(values, ddof=1)) if n > 1 else np.nan
                        sem = float(std / np.sqrt(n)) if n > 1 else np.nan
                        writer.writerow(
                            {
                                "metric": metric,
                                "stage": stage,
                                "delete_lingering": delete_lingering,
                                "group": group,
                                "n_mice": n,
                                "mean": float(np.nanmean(values)) if n else np.nan,
                                "std": std,
                                "sem": sem,
                            }
                        )


def write_anova_summary(rows: list[dict[str, object]]) -> None:
    with ANOVA_CSV.open("w", newline="") as f:
        fieldnames = [
            "metric",
            "stage",
            "delete_lingering",
            "remove_wall",
            "wall_margin",
            "comparison",
            "dzp_n_mice",
            "veh_n_mice",
            "f_statistic",
            "p_value",
            "significant_0_05",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for delete_lingering in DELETE_LINGERING_OPTIONS:
            for stage in STAGE_NAMES:
                for metric in METRIC_NAMES:
                    dzp_values = finite_values(rows, "DZP", stage, delete_lingering, metric)
                    veh_values = finite_values(rows, "VEH", stage, delete_lingering, metric)

                    if len(dzp_values) < 2 or len(veh_values) < 2:
                        f_statistic = np.nan
                        p_value = np.nan
                    else:
                        f_statistic, p_value = f_oneway(dzp_values, veh_values)

                    writer.writerow(
                        {
                            "metric": metric,
                            "stage": stage,
                            "delete_lingering": delete_lingering,
                            "comparison": "DZP_vs_VEH",
                            "dzp_n_mice": len(dzp_values),
                            "veh_n_mice": len(veh_values),
                            "f_statistic": float(f_statistic),
                            "p_value": float(p_value),
                            "significant_0_05": bool(p_value < 0.05) if np.isfinite(p_value) else False,
                        }
                    )


def finite_pathlet_values(
    rows: list[dict[str, object]],
    group: str,
    stage: str,
    delete_lingering: bool,
    remove_wall: bool,
    metric: str,
) -> np.ndarray:
    values = np.asarray(
        [
            float(row[metric])
            for row in rows
            if row["group"] == group
            and row["stage"] == stage
            and row["delete_lingering"] == delete_lingering
            and row["remove_wall"] == remove_wall
        ],
        dtype=float,
    )
    return values[np.isfinite(values)]


def p_to_stars(p_value: float) -> str:
    if not np.isfinite(p_value):
        return ""
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return ""


def write_pathlet_group_summary(rows: list[dict[str, object]]) -> None:
    with PATHLET_GROUP_SUMMARY_CSV.open("w", newline="") as f:
        fieldnames = ["metric", "stage", "delete_lingering", "remove_wall", "wall_margin", "group", "n_pathlets", "mean", "std", "sem"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for delete_lingering in DELETE_LINGERING_OPTIONS:
            for remove_wall in REMOVE_WALL_OPTIONS:
                for stage in PATHLET_STAGE_NAMES:
                    for metric in PATHLET_METRIC_NAMES:
                        for group in ["DZP", "VEH"]:
                            values = finite_pathlet_values(rows, group, stage, delete_lingering, remove_wall, metric)
                            n = len(values)
                            std = float(np.nanstd(values, ddof=1)) if n > 1 else np.nan
                            sem = float(std / np.sqrt(n)) if n > 1 else np.nan
                            writer.writerow(
                                {
                                    "metric": metric,
                                    "stage": stage,
                                    "delete_lingering": delete_lingering,
                                    "remove_wall": remove_wall,
                                    "wall_margin": WALL_MARGIN if remove_wall else 0.0,
                                    "group": group,
                                    "n_pathlets": n,
                                    "mean": float(np.nanmean(values)) if n else np.nan,
                                    "std": std,
                                    "sem": sem,
                                }
                            )


def write_pathlet_anova_summary(rows: list[dict[str, object]]) -> None:
    with PATHLET_ANOVA_CSV.open("w", newline="") as f:
        fieldnames = [
            "metric",
            "stage",
            "delete_lingering",
            "remove_wall",
            "wall_margin",
            "comparison",
            "dzp_n_pathlets",
            "veh_n_pathlets",
            "f_statistic",
            "p_value",
            "significant_0_05",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for delete_lingering in DELETE_LINGERING_OPTIONS:
            for remove_wall in REMOVE_WALL_OPTIONS:
                for stage in PATHLET_STAGE_NAMES:
                    for metric in PATHLET_METRIC_NAMES:
                        dzp_values = finite_pathlet_values(rows, "DZP", stage, delete_lingering, remove_wall, metric)
                        veh_values = finite_pathlet_values(rows, "VEH", stage, delete_lingering, remove_wall, metric)

                        if len(dzp_values) < 2 or len(veh_values) < 2:
                            f_statistic = np.nan
                            p_value = np.nan
                        else:
                            f_statistic, p_value = f_oneway(dzp_values, veh_values)

                        writer.writerow(
                            {
                                "metric": metric,
                                "stage": stage,
                                "delete_lingering": delete_lingering,
                                "remove_wall": remove_wall,
                                "wall_margin": WALL_MARGIN if remove_wall else 0.0,
                                "comparison": "DZP_vs_VEH",
                                "dzp_n_pathlets": len(dzp_values),
                                "veh_n_pathlets": len(veh_values),
                                "f_statistic": float(f_statistic),
                                "p_value": float(p_value),
                                "significant_0_05": bool(p_value < 0.05) if np.isfinite(p_value) else False,
                            }
                        )


def plot_pathlet_group_bars(rows: list[dict[str, object]]) -> list[Path]:
    PATHLET_FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig_paths: list[Path] = []

    for delete_lingering in DELETE_LINGERING_OPTIONS:
        linger_name = "delete_lingering" if delete_lingering else "raw"
        for remove_wall in REMOVE_WALL_OPTIONS:
            wall_name = f"wall_margin_{WALL_MARGIN:g}" if remove_wall else "no_wall_delete"
            option_name = f"{linger_name}_{wall_name}"

            for stage in PATHLET_STAGE_NAMES:
                stage_dir = PATHLET_FIG_DIR / option_name / stage
                stage_dir.mkdir(parents=True, exist_ok=True)

                for metric in PATHLET_METRIC_NAMES:
                    dzp_values = finite_pathlet_values(rows, "DZP", stage, delete_lingering, remove_wall, metric)
                    veh_values = finite_pathlet_values(rows, "VEH", stage, delete_lingering, remove_wall, metric)
                    group_values = [dzp_values, veh_values]
                    means = [float(np.nanmean(values)) if len(values) else np.nan for values in group_values]
                    sems = [
                        float(np.nanstd(values, ddof=1) / np.sqrt(len(values))) if len(values) > 1 else 0.0
                        for values in group_values
                    ]

                    if len(dzp_values) < 2 or len(veh_values) < 2:
                        p_value = np.nan
                    else:
                        _f_statistic, p_value = f_oneway(dzp_values, veh_values)
                    stars = p_to_stars(float(p_value))

                    fig, ax = plt.subplots(figsize=(3.5, 2.3))
                    x = np.arange(2)
                    ax.bar(
                        x,
                        means,
                        yerr=sems,
                        width=0.62,
                        color=[GROUP_COLORS["DZP"], GROUP_COLORS["VEH"]],
                        edgecolor="black",
                        linewidth=0.8,
                        capsize=3,
                        alpha=0.9,
                    )

                    finite_means = [value for value in means if np.isfinite(value)]
                    finite_tops = [mean + sem for mean, sem in zip(means, sems) if np.isfinite(mean)]
                    if finite_tops:
                        y_top = max(finite_tops)
                        y_min, y_max = ax.get_ylim()
                        padding = 0.08 * (y_max - y_min if y_max > y_min else 1.0)
                        if stars:
                            ax.plot(
                                [0, 0, 1, 1],
                                [y_top + padding, y_top + 1.35 * padding, y_top + 1.35 * padding, y_top + padding],
                                color="black",
                                linewidth=0.8,
                            )
                            ax.text(0.5, y_top + 1.45 * padding, stars, ha="center", va="bottom", fontsize=10)
                            ax.set_ylim(y_min, y_top + 3.0 * padding)
                        elif finite_means:
                            ax.set_ylim(y_min, y_max + 0.05 * (y_max - y_min if y_max > y_min else 1.0))

                    ax.set_xticks(x)
                    ax.set_xticklabels(["DZP", "VEH"])
                    ax.set_ylabel(METRIC_LABELS.get(metric, metric.replace("_", " ")))
                    ax.set_title(stage.replace("_", " "))
                    ax.spines["top"].set_visible(False)
                    ax.spines["right"].set_visible(False)
                    fig.tight_layout(pad=0.6)

                    fig_path = stage_dir / f"{metric}_{stage}_{option_name}_pathlet_DZP_vs_VEH.png"
                    fig.savefig(fig_path, dpi=300)
                    plt.close(fig)
                    fig_paths.append(fig_path)

    return fig_paths

def make_mat_arrays(rows: list[dict[str, object]]) -> dict[str, np.ndarray]:
    """Create MATLAB-friendly arrays with shape mice x stages x delete_lingering_options."""
    mat: dict[str, np.ndarray] = {
        "mice": np.asarray(MICE, dtype=object),
        "stage_names": np.asarray(STAGE_NAMES, dtype=object),
        "delete_lingering_options": np.asarray(DELETE_LINGERING_OPTIONS, dtype=object),
    }

    row_lookup = {
        (row["mouse"], row["stage"], row["delete_lingering"]): row
        for row in rows
    }

    for metric in METRIC_NAMES:
        arr = np.full((len(MICE), len(STAGE_NAMES), len(DELETE_LINGERING_OPTIONS)), np.nan, dtype=float)
        for mouse_index, mouse_name in enumerate(MICE):
            for stage_index, stage in enumerate(STAGE_NAMES):
                for opt_index, delete_lingering in enumerate(DELETE_LINGERING_OPTIONS):
                    row = row_lookup.get((mouse_name, stage, delete_lingering))
                    if row is not None:
                        arr[mouse_index, stage_index, opt_index] = float(row[metric])
        mat[metric] = arr

    return mat


def all_mouse_values(rows: list[dict[str, object]], stage: str, delete_lingering: bool, remove_wall: bool, metric: str) -> np.ndarray:
    values = np.asarray(
        [
            float(row[metric])
            for row in rows
            if row["stage"] == stage
            and row["delete_lingering"] == delete_lingering
            and row["remove_wall"] == remove_wall
        ],
        dtype=float,
    )
    return values[np.isfinite(values)]


def write_quarter_summary(rows: list[dict[str, object]]) -> None:
    with QUARTER_SUMMARY_CSV.open("w", newline="") as f:
        fieldnames = ["metric", "stage", "delete_lingering", "remove_wall", "wall_margin", "n_pathlets", "mean", "std", "sem"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for delete_lingering in DELETE_LINGERING_OPTIONS:
            for remove_wall in REMOVE_WALL_OPTIONS:
                for metric in METRIC_NAMES:
                    for stage in STAGE_NAMES:
                        values = all_mouse_values(rows, stage, delete_lingering, remove_wall, metric)
                        n = len(values)
                        std = float(np.nanstd(values, ddof=1)) if n > 1 else np.nan
                        sem = float(std / np.sqrt(n)) if n > 1 else np.nan
                        writer.writerow({
                            "metric": metric,
                            "stage": stage,
                            "delete_lingering": delete_lingering,
                            "remove_wall": remove_wall,
                            "wall_margin": WALL_MARGIN if remove_wall else 0.0,
                            "n_pathlets": n,
                            "mean": float(np.nanmean(values)) if n else np.nan,
                            "std": std,
                            "sem": sem,
                        })


def write_quarter_time_effect_anova(rows: list[dict[str, object]]) -> None:
    anova_rows: list[dict[str, object]] = []
    for delete_lingering in DELETE_LINGERING_OPTIONS:
        for remove_wall in REMOVE_WALL_OPTIONS:
            for metric in METRIC_NAMES:
                stage_values = [
                    all_mouse_values(rows, stage, delete_lingering, remove_wall, metric)
                    for stage in STAGE_NAMES
                ]
                total_n = sum(len(values) for values in stage_values)
                df_between = len(stage_values) - 1
                df_within = total_n - len(stage_values)
                if all(len(values) > 1 for values in stage_values):
                    f_statistic, p_value = f_oneway(*stage_values)
                    f_statistic = float(f_statistic)
                    p_value = float(p_value)
                else:
                    f_statistic = np.nan
                    p_value = np.nan
                    df_within = np.nan

                anova_rows.append({
                    "effect": "time",
                    "metric": metric,
                    "delete_lingering": delete_lingering,
                    "remove_wall": remove_wall,
                    "wall_margin": WALL_MARGIN if remove_wall else 0.0,
                    "comparison": "quarter_1_vs_quarter_2_vs_quarter_3_vs_quarter_4",
                    "n_quarter_1": len(stage_values[0]),
                    "n_quarter_2": len(stage_values[1]),
                    "n_quarter_3": len(stage_values[2]),
                    "n_quarter_4": len(stage_values[3]),
                    "df_between": df_between,
                    "df_within": df_within,
                    "f_statistic": f_statistic,
                    "p_value": p_value,
                    "significant_0_05": bool(np.isfinite(p_value) and p_value < 0.05),
                })

    with QUARTER_ANOVA_CSV.open("w", newline="") as f:
        fieldnames = [
            "effect",
            "metric",
            "delete_lingering",
            "remove_wall",
            "wall_margin",
            "comparison",
            "n_quarter_1",
            "n_quarter_2",
            "n_quarter_3",
            "n_quarter_4",
            "df_between",
            "df_within",
            "f_statistic",
            "p_value",
            "significant_0_05",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(anova_rows)

    if anova_rows:
        print("\nQuarter time-effect one-way ANOVA (time-defined pathlets, filtered inside pathlets)")
        print(
            f"{'variable':<22} {'wall':>6} {'Q1_n':>7} {'Q2_n':>7} {'Q3_n':>7} {'Q4_n':>7} "
            f"{'df':>12} {'F':>12} {'p':>12} {'sig_0.05':>10}"
        )
        print("-" * 115)
        for row in anova_rows:
            df_between = row["df_between"]
            df_within = row["df_within"]
            df_text = (
                f"({int(df_between)}, {int(df_within)})"
                if np.isfinite(df_between) and np.isfinite(df_within)
                else "(nan, nan)"
            )
            print(
                f"{str(row['metric']):<22} "
                f"{str(row['remove_wall']):>6} "
                f"{int(row['n_quarter_1']):>7} "
                f"{int(row['n_quarter_2']):>7} "
                f"{int(row['n_quarter_3']):>7} "
                f"{int(row['n_quarter_4']):>7} "
                f"{df_text:>12} "
                f"{float(row['f_statistic']):>12.6g} "
                f"{float(row['p_value']):>12.6g} "
                f"{str(row['significant_0_05']):>10}"
            )
        print()


def plot_metric_group_means(rows: list[dict[str, object]]) -> list[Path]:
    QUARTER_FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig_paths: list[Path] = []
    x = np.arange(len(STAGE_NAMES))

    for delete_lingering in DELETE_LINGERING_OPTIONS:
        linger_name = "delete_lingering" if delete_lingering else "raw"
        for remove_wall in REMOVE_WALL_OPTIONS:
            wall_name = f"wall_margin_{WALL_MARGIN:g}" if remove_wall else "no_wall_delete"
            option_name = f"time_pathlets_{linger_name}_{wall_name}"
            for metric in METRIC_NAMES:
                all_means = []
                dzp_means = []
                veh_means = []
                all_sems = []
                dzp_sems = []
                veh_sems = []
                for stage in STAGE_NAMES:
                    all_values = all_mouse_values(rows, stage, delete_lingering, remove_wall, metric)
                    dzp_values = finite_pathlet_values(rows, "DZP", stage, delete_lingering, remove_wall, metric)
                    veh_values = finite_pathlet_values(rows, "VEH", stage, delete_lingering, remove_wall, metric)
                    all_means.append(float(np.nanmean(all_values)) if len(all_values) else np.nan)
                    dzp_means.append(float(np.nanmean(dzp_values)) if len(dzp_values) else np.nan)
                    veh_means.append(float(np.nanmean(veh_values)) if len(veh_values) else np.nan)
                    all_sems.append(float(np.nanstd(all_values, ddof=1) / np.sqrt(len(all_values))) if len(all_values) > 1 else 0.0)
                    dzp_sems.append(float(np.nanstd(dzp_values, ddof=1) / np.sqrt(len(dzp_values))) if len(dzp_values) > 1 else 0.0)
                    veh_sems.append(float(np.nanstd(veh_values, ddof=1) / np.sqrt(len(veh_values))) if len(veh_values) > 1 else 0.0)

                fig, ax = plt.subplots(figsize=(3, 2))
                ax.errorbar(x, all_means, yerr=all_sems, marker="o", markersize=3.5, linewidth=1.4, elinewidth=0.8, capsize=2, color="black")
                ax.errorbar(x, dzp_means, yerr=dzp_sems, marker="o", markersize=3.2, linewidth=1.2, elinewidth=0.8, capsize=2, color=GROUP_COLORS["DZP"])
                ax.errorbar(x, veh_means, yerr=veh_sems, marker="o", markersize=3.2, linewidth=1.2, elinewidth=0.8, capsize=2, color=GROUP_COLORS["VEH"])
                ax.set_xticks(x)
                ax.set_xticklabels(QUARTER_LABELS, fontsize=8)
                ax.set_ylabel(METRIC_LABELS.get(metric, metric.replace("_", " ")), fontsize=10)
                ax.tick_params(axis="both", labelsize=8)
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                fig.tight_layout(pad=0.7)

                fig_path = QUARTER_FIG_DIR / f"{metric}_{option_name}_quarters_all_DZP_VEH_lines.png"
                fig.savefig(fig_path, dpi=300)
                svg_path = fig_path.with_suffix(".svg")
                fig.savefig(svg_path)
                plt.close(fig)
                fig_paths.append(fig_path)
                fig_paths.append(svg_path)

    return fig_paths

# =========================
# Main
# =========================
def main() -> None:
    start_time = time.perf_counter()
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    QUARTER_FIG_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading tracks...")
    all_tracks = {mouse_name: load_track(mouse_name) for mouse_name in MICE}
    arena = build_arena(all_tracks)

    rows: list[dict[str, object]] = []
    for mouse_name, raw_path in all_tracks.items():
        print(f"Processing {mouse_name}...")
        group = group_for_mouse(mouse_name)

        wall_center, wall_radius = mouse_wall_geometry(raw_path)
        for stage, raw_stage_path in split_full_and_quarters(raw_path).items():
            if stage == "full":
                continue
            quarter_stage = stage.replace("period", "quarter")
            for delete_lingering in DELETE_LINGERING_OPTIONS:
                quarter_path = remove_lingering(raw_stage_path) if delete_lingering else raw_stage_path.copy()
                for pathlet_index, quarter_pathlet in iter_full_track_pathlets(quarter_path):
                    for remove_wall in REMOVE_WALL_OPTIONS:
                        if remove_wall:
                            filtered_pathlet = remove_near_wall_points(quarter_pathlet, wall_center, wall_radius)
                        else:
                            filtered_pathlet = quarter_pathlet.copy()
                        if len(filtered_pathlet) != PATHLET_STEP_LENGTH:
                            continue
                        rows.append({
                            "mouse": mouse_name,
                            "group": group,
                            "delete_lingering": delete_lingering,
                            "remove_wall": remove_wall,
                            "wall_margin": WALL_MARGIN if remove_wall else 0.0,
                            "stage": quarter_stage,
                            "pathlet_index": pathlet_index,
                            "n_points_raw_pathlet": len(quarter_pathlet),
                            "n_points_after_lingering": len(quarter_pathlet),
                            "n_points_after_wall": len(filtered_pathlet),
                            **compute_pathlet_metrics(filtered_pathlet, arena),
                        })

    with QUARTER_PATHLET_CSV.open("w", newline="") as f:
        fieldnames = [
            "mouse",
            "group",
            "delete_lingering",
            "remove_wall",
            "wall_margin",
            "stage",
            "pathlet_index",
            "n_points_raw_pathlet",
            "n_points_after_lingering",
            "n_points_after_wall",
            *METRIC_NAMES,
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    write_quarter_summary(rows)
    write_quarter_time_effect_anova(rows)
    fig_paths = plot_metric_group_means(rows)

    elapsed = time.perf_counter() - start_time
    print(f"Saved pooled pathlet quarter CSV: {QUARTER_PATHLET_CSV}")
    print(f"Saved pooled pathlet quarter summary CSV: {QUARTER_SUMMARY_CSV}")
    print(f"Saved pooled pathlet quarter ANOVA CSV: {QUARTER_ANOVA_CSV}")
    print(f"Saved {len(fig_paths)} quarter figures in: {QUARTER_FIG_DIR}")
    print(f"Elapsed seconds: {elapsed:.2f}")

if __name__ == "__main__":
    main()
