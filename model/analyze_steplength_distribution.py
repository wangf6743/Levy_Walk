# this code analyzes the step length distribution of
# simulated trajectories by quarter and runs the MLE workflow on each quarter,
# which is same as the experimental data analysis.

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib_cache"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(__file__).resolve().parent / ".cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
SIMULATION_DIR = SCRIPT_DIR / "data_simulation"  # the folder where the simulation data are stored
DEFAULT_OUT_DIR = SIMULATION_DIR / "analysis" / "steplength_distribution_N_neuron"
MLE_DIR = SCRIPT_DIR.parent / "data_for_analysis" / "mle_distributions_python"

sys.path.insert(0, str(MLE_DIR))
import model.MLE_fit_seperate_model as mle_wallhugger


def alpha_from_path(path: Path) -> str:
    stem = path.stem
    if stem.startswith("alpha_"):
        return stem[len("alpha_") :].replace("p", ".").replace("minus_", "-")
    return stem


def load_simulation_csv(path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    data = np.genfromtxt(path, delimiter=",", names=True)
    if data.ndim == 0:
        data = np.array([data])

    step = np.asarray(data["step"], dtype=float)
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    valid = np.isfinite(step) & np.isfinite(x) & np.isfinite(y)
    return step[valid], x[valid], y[valid]


def n_from_path(path: Path) -> str:
    name = path.name
    if name.startswith("N_"):
        return name[len("N_") :]
    return name


def sort_n_key(n_value: object) -> Tuple[int, object]:
    try:
        return 0, int(str(n_value))
    except ValueError:
        try:
            return 0, float(str(n_value))
        except ValueError:
            return 1, str(n_value)


def n_dirs(input_dir: Path, neuron_counts: Optional[List[str]] = None) -> List[Path]:
    dirs = sorted(
        [path for path in input_dir.glob("N_*") if path.is_dir()],
        key=lambda path: sort_n_key(n_from_path(path)),
    )
    if neuron_counts:
        n_set = set(neuron_counts)
        dirs = [path for path in dirs if path.name in n_set or n_from_path(path) in n_set]
    return dirs


def safe_n_filename(n_value: str) -> str:
    return n_value.replace("-", "minus_").replace(".", "p")


def simulation_files(input_dir: Path, trials: Optional[List[str]] = None) -> List[Path]:
    alpha_files = sorted(input_dir.glob("trial_*/alpha_*.csv"))
    if alpha_files:
        files = alpha_files
    else:
        files = sorted(input_dir.glob("trial_*/*.csv"))

    if trials:
        trial_set = set(trials)
        files = [path for path in files if path.parent.name in trial_set]
    return files


def plot_quarter_trajectories(
    periods: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray]],
    fig_path: Path,
    title: str,
    radius: float,
    center: np.ndarray,
) -> None:
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(8, 8), constrained_layout=True)
    axes_flat = axes.ravel()
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    theta = np.linspace(0, 2.0 * np.pi, 361)
    arena_x = center[0] + radius * np.cos(theta)
    arena_y = center[1] + radius * np.sin(theta)

    for ax, (period, _times, x, y), color in zip(axes_flat, periods, colors):
        ax.plot(arena_x, arena_y, color="#888888", linewidth=0.8)
        ax.plot(x, y, color=color, linewidth=0.7)
        if len(x):
            ax.scatter(x[0], y[0], s=12, color="black", zorder=3)
            ax.scatter(x[-1], y[-1], s=12, color=color, zorder=3)
        ax.set_title(period)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(center[0] - radius - 3.0, center[0] + radius + 3.0)
        ax.set_ylim(center[1] - radius - 3.0, center[1] + radius + 3.0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(title)
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)


def build_result_row(
    n_value: str,
    trial: str,
    alpha: str,
    source_file: Path,
    period: str,
    wall_margin: float,
    dimension: str,
    n_points_before_filter: int,
    n_points_after_linger_filter: int,
    n_points_after_wall_filter: int,
    radius: float,
    steps: np.ndarray,
    exp_result,
    tp_result,
    label: str,
) -> Dict[str, object]:
    base = mle_wallhugger.result_row(
        mouse=f"N_{n_value}_{trial}_{alpha}",
        period=period,
        wall_margin=wall_margin,
        dimension=dimension,
        n_points_before_filter=n_points_before_filter,
        n_points_after_wall_filter=n_points_after_wall_filter,
        n_points_after_linger_filter=n_points_after_linger_filter,
        radius=radius,
        steps=steps,
        exp_result=exp_result,
        tp_result=tp_result,
        label=label,
    )
    return {
        "N": n_value,
        "trial": trial,
        "alpha": alpha,
        "source_file": str(source_file),
        **base,
    }


def write_rows(rows: List[Dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError("No MLE rows were produced.")

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def sort_alpha_key(alpha: object) -> Tuple[int, object]:
    try:
        return 0, float(str(alpha))
    except ValueError:
        return 1, str(alpha)


def print_tp_summary(rows: List[Dict[str, object]]) -> None:
    print("\nTP summary by N, alpha, and period")
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            sort_n_key(row["N"]),
            str(row["trial"]),
            sort_alpha_key(row["alpha"]),
            str(row["period"]),
            str(row["dimension"]),
            float(row["wall_margin"]),
        ),
    )
    for row in sorted_rows:
        is_tp = "TP" if row["is_tp"] else "not TP"
        print(
            f"  N={row['N']} | {row['trial']} | alpha={row['alpha']} | {row['period']} | "
            f"dimension={row['dimension']} | wall_margin={row['wall_margin']} -> {is_tp}"
        )


def plot_tp_percentage_for_n(rows: List[Dict[str, object]], n_value: str, fig_path: Path) -> None:
    n_rows = [row for row in rows if str(row["N"]) == n_value]
    if not n_rows:
        return

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    periods = sorted({str(row["period"]) for row in n_rows})
    alphas = sorted({str(row["alpha"]) for row in n_rows}, key=sort_alpha_key)
    counts = {
        (period, alpha): {"tp": 0, "total": 0}
        for period in periods
        for alpha in alphas
    }

    for row in n_rows:
        key = (str(row["period"]), str(row["alpha"]))
        counts[key]["total"] += 1
        if row["classification"] == "TP":
            counts[key]["tp"] += 1

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    colors = ["#4477aa", "#cc6677", "#228833", "#aa3377"]
    x = np.arange(len(alphas))

    for ax, period, color in zip(axes.ravel(), periods, colors):
        percentages = []
        labels = []
        for alpha in alphas:
            total = counts[(period, alpha)]["total"]
            tp = counts[(period, alpha)]["tp"]
            percentages.append(100.0 * tp / total if total else 0.0)
            labels.append(f"{tp}/{total}")

        bars = ax.bar(x, percentages, color=color, alpha=0.85)
        ax.set_title(period)
        ax.set_xlabel("alpha")
        ax.set_ylabel("TP percentage (%)")
        ax.set_xticks(x)
        ax.set_xticklabels(alphas, rotation=45, ha="right")
        ax.set_ylim(0.0, 100.0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color="#dddddd", linewidth=0.7)

        for bar, label in zip(bars, labels):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                min(height + 2.0, 98.0),
                label,
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=90,
            )

    for ax in axes.ravel()[len(periods):]:
        ax.set_visible(False)

    fig.suptitle(f"TP percentage by alpha and period, N={n_value}")
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)


def plot_tp_percentage_by_n(rows: List[Dict[str, object]], output_dir: Path) -> List[Path]:
    fig_paths: List[Path] = []
    n_values = sorted({str(row["N"]) for row in rows}, key=sort_n_key)
    for n_value in n_values:
        fig_path = output_dir / f"tp_percentage_N_{safe_n_filename(n_value)}_by_period_alpha.png"
        plot_tp_percentage_for_n(rows, n_value, fig_path)
        fig_paths.append(fig_path)
    return fig_paths


def analyze_file(
    csv_path: Path,
    n_value: str,
    args: argparse.Namespace,
    fig_dir: Path,
) -> List[Dict[str, object]]:
    trial = csv_path.parent.name
    alpha = alpha_from_path(csv_path)
    times, x, y = load_simulation_csv(csv_path)

    center = np.array([args.center_x, args.center_y], dtype=float)
    radius = float(args.radius)
    periods = mle_wallhugger.quarter_track_periods(times, x, y)

    fig_path = fig_dir / f"N_{safe_n_filename(n_value)}" / trial / f"{csv_path.stem}_periods.png"
    plot_quarter_trajectories(
        periods=periods,
        fig_path=fig_path,
        title=f"N={n_value}, {trial}, alpha={alpha}",
        radius=radius,
        center=center,
    )

    rows: List[Dict[str, object]] = []
    for wall_margin in args.wall_margins:
        for period, _period_times, period_x, period_y in periods:
            n_points_before_filter = len(period_x)

            if mle_wallhugger.REMOVE_LINGER_POINTS:
                linger_x, linger_y = mle_wallhugger.remove_lingering_points(period_x, period_y)
            else:
                linger_x, linger_y = period_x, period_y
            n_points_after_linger_filter = len(linger_x)

            if mle_wallhugger.REMOVE_WALL_POINTS:
                fit_x, fit_y = mle_wallhugger.remove_wall_and_combine_pathlets(
                    linger_x,
                    linger_y,
                    radius,
                    center,
                    wall_margin,
                )
            else:
                fit_x, fit_y = linger_x, linger_y
            n_points_after_wall_filter = len(fit_x)

            for dimension in args.dimensions:
                steps = mle_wallhugger.make_steps(fit_x, fit_y, dimension)
                if len(steps) < 2:
                    continue

                exp_result, tp_result, label = mle_wallhugger.fit_half(steps)
                rows.append(
                    build_result_row(
                        n_value=n_value,
                        trial=trial,
                        alpha=alpha,
                        source_file=csv_path,
                        period=period,
                        wall_margin=wall_margin,
                        dimension=dimension,
                        n_points_before_filter=n_points_before_filter,
                        n_points_after_linger_filter=n_points_after_linger_filter,
                        n_points_after_wall_filter=n_points_after_wall_filter,
                        radius=radius,
                        steps=steps,
                        exp_result=exp_result,
                        tp_result=tp_result,
                        label=label,
                    )
                )

    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot N-neuron simulated trajectories by quarter and run the wall-hugger MLE workflow."
    )
    parser.add_argument("--input-dir", type=Path, default=SIMULATION_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--neuron-counts",
        nargs="+",
        default=None,
        help="optional N folders or values, e.g. N_10 100",
    )
    parser.add_argument("--dimensions", nargs="+", default=mle_wallhugger.DIMENSIONS)
    parser.add_argument("--wall-margins", nargs="+", type=float, default=mle_wallhugger.WALL_MARGINS)
    parser.add_argument("--radius", type=float, default=90.0)
    parser.add_argument("--center-x", type=float, default=90.0)
    parser.add_argument("--center-y", type=float, default=90.0)
    parser.add_argument("--p-value-tests", type=int, default=mle_wallhugger.P_VALUE_TESTS)
    parser.add_argument("--no-p-test", action="store_true", help="skip Monte Carlo p-value tests")
    parser.add_argument("--remove-lingering", action="store_true", help="remove lingering points before fitting")
    parser.add_argument("--max-files", type=int, default=None, help="optional limit for quick testing")
    parser.add_argument("--trials", nargs="+", default=None, help="trial folders to analyze, for example trial_01")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mle_wallhugger.P_TEST = not args.no_p_test
    mle_wallhugger.P_VALUE_TESTS = args.p_value_tests
    mle_wallhugger.REMOVE_LINGER_POINTS = args.remove_lingering

    directories = n_dirs(args.input_dir, args.neuron_counts)
    if directories:
        files_with_n: List[Tuple[Path, str]] = []
        for n_dir in directories:
            files_with_n.extend((path, n_from_path(n_dir)) for path in simulation_files(n_dir, args.trials))
    else:
        files = simulation_files(args.input_dir, args.trials)
        files_with_n = [(path, n_from_path(args.input_dir)) for path in files]

    if args.max_files is not None:
        files_with_n = files_with_n[: args.max_files]
    if not files_with_n:
        raise FileNotFoundError(f"No N-neuron simulation CSV files found in {args.input_dir}")

    fig_dir = args.output_dir / "trajectory_period_figs"
    rows: List[Dict[str, object]] = []

    print(f"Input: {args.input_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Files: {len(files_with_n)}")
    print(f"N values: {sorted({n_value for _path, n_value in files_with_n}, key=sort_n_key)}")
    if args.trials:
        print(f"Trials: {args.trials}")
    print(f"Dimensions: {args.dimensions}")
    print(f"Wall margins: {args.wall_margins}")
    print(f"P-test: {mle_wallhugger.P_TEST}, n_tests: {mle_wallhugger.P_VALUE_TESTS}")

    for index, (csv_path, n_value) in enumerate(files_with_n, start=1):
        file_rows = analyze_file(csv_path, n_value, args, fig_dir)
        rows.extend(file_rows)
        print(f"[{index}/{len(files_with_n)}] N={n_value} {csv_path}: {len(file_rows)} MLE rows")

    out_file = args.output_dir / "N_neuron_quarter_mle_results.csv"
    write_rows(rows, out_file)
    tp_period_figs = plot_tp_percentage_by_n(rows, args.output_dir)

    tp_count = sum(row["classification"] == "TP" for row in rows)
    total = len(rows)
    tp_percent = 100.0 * tp_count / total if total else math.nan
    print(f"N values analyzed: {len({str(row['N']) for row in rows})}")
    print(f"Saved MLE results: {out_file}")
    print(f"Saved trajectory figures: {fig_dir}")
    for tp_period_fig in tp_period_figs:
        print(f"Saved TP percentage histogram: {tp_period_fig}")
    print(f"TP percentage: {tp_percent:.2f}% ({tp_count}/{total})")
    print_tp_summary(rows)


if __name__ == "__main__":
    main()
