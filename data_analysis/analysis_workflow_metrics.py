
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


# =========================
# Paths
# =========================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
OUT_DIR = SCRIPT_DIR / "data_index"
CSV_DIR = SCRIPT_DIR / "behabiral_metrices"
FIG_DIR = OUT_DIR / "workflow_metric_figs"

PER_MOUSE_CSV = CSV_DIR / "workflow_metrics_full_and_quarters.csv"
GROUP_SUMMARY_CSV = CSV_DIR / "workflow_metrics_group_summary.csv"
ANOVA_CSV = CSV_DIR / "workflow_metrics_group_anova.csv"
MAT_PATH = OUT_DIR / "workflow_metrics_full_and_quarters.mat"


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
LINGER_RATE_THRESHOLD = 0.05

# The workflow asks for delete lingering data to be an option.
# This script calculates both versions: raw and delete_lingering.
DELETE_LINGERING_OPTIONS = [False, True]

STAGE_NAMES = ["full", "period_1", "period_2", "period_3", "period_4"]
METRIC_NAMES = ["msd", "spatial_coverage", "exploration_entropy", "local_cumulative_entropy", "sda", "mean_speed", "std_speed"]


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
    radius = min(max_x - min_x, max_y - min_y) / 2.0

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
    return float(np.sum(visited_circular_bins) / n_circular_bins)


def compute_exploration_entropy(path: np.ndarray, arena: dict[str, np.ndarray | float]) -> tuple[float, float]:
    """
    Cumulative occupancy entropy over spatial bins.

    Returns two entropy measures:
    1. Global cumulative entropy: based on all spatial occupancy in the full path
       O_i = C_i / sum_j C_j
       E = -sum_i O_i * log2(O_i)
    
    2. Local cumulative entropy: mean entropy computed over sliding windows (±100 steps)
       For each time point t (excluding edges where window is incomplete):
       C_l(i,t) = count of visits to bin i in window [t-100, t+100]
       O_l(i,t) = C_l(i,t) / sum_j C_l(j,t)
       E_l(t) = -sum_i O_l(i,t) * log2(O_l(i,t))
       Return: mean(E_l(t)) across valid time points
    
    Note: Points in first and last 100 steps don't have complete windows,
    so local entropy is only computed for the middle section of the path.
    """
    circular_bin_mask = np.asarray(arena["circular_bin_mask"], dtype=bool)
    n_circular_bins = int(np.sum(circular_bin_mask))
    if n_circular_bins <= 1 or len(path) == 0:
        return np.nan, np.nan

    # ===== Global cumulative entropy =====
    counts = compute_occupancy_counts(path, arena)
    circular_counts = counts[circular_bin_mask]
    total_counts = float(np.sum(circular_counts))
    if total_counts <= 0:
        return np.nan, np.nan

    prob = circular_counts / total_counts
    prob = prob[prob > 0]
    cumulative_entropy = float(-np.sum(prob * np.log2(prob)))
    
    # ===== Local cumulative entropy with sliding window =====
    window_half = 100
    local_entropies = []
    
    # Only compute for time points with complete windows
    for t in range(window_half, len(path) - window_half):
        # Extract window [t-100, t+100]
        window_path = path[t - window_half:t + window_half + 1]
        
        # Compute occupancy counts for this window
        local_counts = compute_occupancy_counts(window_path, arena)
        local_circular_counts = local_counts[circular_bin_mask]
        local_total = float(np.sum(local_circular_counts))
        
        if local_total > 0:
            local_prob = local_circular_counts / local_total
            local_prob = local_prob[local_prob > 0]
            if len(local_prob) > 0:
                local_entropy = float(-np.sum(local_prob * np.log2(local_prob)))
                local_entropies.append(local_entropy)
    
    # Return mean of local entropies, or nan if no valid windows
    if len(local_entropies) > 0:
        local_cumulative_entropy = float(np.nanmean(local_entropies))
    else:
        local_cumulative_entropy = np.nan
    
    return cumulative_entropy, local_cumulative_entropy


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


def compute_speed_stats(path: np.ndarray) -> tuple[float, float]:
    """Mean and sample standard deviation of step speed/displacement."""
    if len(path) < 2:
        return np.nan, np.nan

    rate, _angle = comput_traject_polar(path[:, 0], path[:, 1])
    rate = rate[np.isfinite(rate)]
    if len(rate) == 0:
        return np.nan, np.nan

    mean_speed = float(np.nanmean(rate))
    std_speed = float(np.nanstd(rate, ddof=1)) if len(rate) > 1 else 0.0
    return mean_speed, std_speed


def compute_all_metrics(path: np.ndarray, arena: dict[str, np.ndarray | float]) -> dict[str, float]:
    cumulative_entropy, local_cumulative_entropy = compute_exploration_entropy(path, arena)
    mean_speed, std_speed = compute_speed_stats(path)
    return {
        "msd": compute_msd(path),
        "spatial_coverage": compute_spatial_coverage(path, arena),
        "exploration_entropy": cumulative_entropy,
        "local_cumulative_entropy": local_cumulative_entropy,
        "sda": compute_sda(path),
        "mean_speed": mean_speed,
        "std_speed": std_speed,
    }


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


def plot_metric_group_means(rows: list[dict[str, object]]) -> list[Path]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig_paths: list[Path] = []

    for delete_lingering in DELETE_LINGERING_OPTIONS:
        option_name = "delete_lingering" if delete_lingering else "raw"
        for metric in METRIC_NAMES:
            for stage in STAGE_NAMES:
                groups = ["DZP", "VEH"]
                group_values = [finite_values(rows, group, stage, delete_lingering, metric) for group in groups]
                means = [float(np.nanmean(values)) if len(values) else np.nan for values in group_values]
                sems = [
                    float(np.nanstd(values, ddof=1) / np.sqrt(len(values))) if len(values) > 1 else 0.0
                    for values in group_values
                ]

                fig_path = FIG_DIR / f"{metric}_{stage}_{option_name}_DZP_vs_VEH.png"
                fig, ax = plt.subplots(figsize=(4.2, 4.2))
                x = np.arange(len(groups))
                ax.bar(x, means, yerr=sems, width=0.65, edgecolor="black", capsize=4)
                ax.set_xticks(x)
                ax.set_xticklabels(groups, fontname="Times New Roman", fontsize=12)
                ax.set_ylabel(metric.replace("_", " "), fontname="Times New Roman", fontsize=13)
                ax.set_title(f"{stage.replace('_', ' ')} | {option_name}", fontname="Times New Roman", fontsize=13)
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                fig.tight_layout()
                fig.savefig(fig_path, dpi=300)
                plt.close(fig)
                fig_paths.append(fig_path)

    return fig_paths


# =========================
# Main
# =========================
def main() -> None:
    start_time = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading tracks...")
    all_tracks = {mouse_name: load_track(mouse_name) for mouse_name in MICE}
    arena = build_arena(all_tracks)

    rows: list[dict[str, object]] = []
    for mouse_name, raw_path in all_tracks.items():
        print(f"Processing {mouse_name}...")
        group = group_for_mouse(mouse_name)

        for delete_lingering in DELETE_LINGERING_OPTIONS:
            path_for_analysis = remove_lingering(raw_path) if delete_lingering else raw_path.copy()
            stage_paths = split_full_and_quarters(path_for_analysis)

            for stage_name, stage_path in stage_paths.items():
                metrics = compute_all_metrics(stage_path, arena)
                rows.append(
                    {
                        "mouse": mouse_name,
                        "group": group,
                        "delete_lingering": delete_lingering,
                        "stage": stage_name,
                        **metrics,
                    }
                )

    write_per_mouse_csv(rows)
    write_group_summary(rows)
    write_anova_summary(rows)
    savemat(MAT_PATH, make_mat_arrays(rows))
    fig_paths = plot_metric_group_means(rows)

    elapsed = time.perf_counter() - start_time
    print(f"Saved per-mouse metrics CSV: {PER_MOUSE_CSV}")
    print(f"Saved group summary CSV: {GROUP_SUMMARY_CSV}")
    print(f"Saved ANOVA CSV: {ANOVA_CSV}")
    print(f"Saved MAT: {MAT_PATH}")
    print(f"Saved {len(fig_paths)} group mean figures in: {FIG_DIR}")
    print(f"Elapsed seconds: {elapsed:.2f}")


if __name__ == "__main__":
    main()
