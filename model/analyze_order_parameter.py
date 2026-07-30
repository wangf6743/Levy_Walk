import argparse
import csv
import math
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib_cache"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(__file__).resolve().parent / ".cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
SIMULATION_DIR = SCRIPT_DIR / "data_simulation" # the folder where the simulation data are stored
DEFAULT_OUT_DIR = SIMULATION_DIR / "analysis" / "order_parameter"

METRIC_LABELS = {
    "mental_r_mean": "mental_r mean",
    "dif_angle_std": "dif_angle standard deviation",
}

PERIOD_LABELS = {
    "whole_trial": "whole trial",
    "last_3_4": "last 3/4 trial",
}


def alpha_from_path(path: Path) -> str:
    stem = path.stem
    if stem.startswith("alpha_"):
        return stem[len("alpha_") :].replace("p", ".").replace("minus_", "-")
    return stem


def sort_alpha_key(alpha: object) -> Tuple[int, object]:
    try:
        return 0, float(str(alpha))
    except ValueError:
        return 1, str(alpha)


def simulation_files(input_dir: Path, trials: Optional[List[str]] = None) -> List[Path]:
    files = sorted(input_dir.glob("trial_*/alpha_*.csv"))
    if not files:
        files = sorted(input_dir.glob("trial_*/*.csv"))

    if trials:
        trial_set = set(trials)
        files = [path for path in files if path.parent.name in trial_set]
    return files


def load_columns(csv_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    with csv_path.open() as f:
        header = f.readline().strip().split(",")

    names = set(header)
    missing = {"mental_r", "dif_angle"} - names
    if missing:
        raise ValueError(f"{csv_path} is missing columns: {sorted(missing)}")

    dif_angle_col = header.index("dif_angle")
    mental_r_col = header.index("mental_r")
    data = np.loadtxt(
        csv_path,
        delimiter=",",
        skiprows=1,
        usecols=(mental_r_col, dif_angle_col),
    )
    if data.ndim == 1:
        data = data.reshape(1, -1)

    return data[:, 0], data[:, 1]


def finite_or_nan(values: Iterable[float], stat: str) -> float:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return math.nan
    if stat == "mean":
        return float(np.mean(arr))
    if stat == "std":
        return float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    raise ValueError(f"Unknown stat: {stat}")


def sem(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) <= 1:
        return 0.0 if len(arr) == 1 else math.nan
    return float(np.std(arr, ddof=1) / np.sqrt(len(arr)))


def analyze_file(csv_path: Path) -> List[Dict[str, object]]:
    trial = csv_path.parent.name
    alpha = alpha_from_path(csv_path)
    mental_r, dif_angle = load_columns(csv_path)
    start_last_3_4 = len(mental_r) // 4

    periods = {
        "whole_trial": (mental_r, dif_angle),
        "last_3_4": (mental_r[start_last_3_4:], dif_angle[start_last_3_4:]),
    }

    rows: List[Dict[str, object]] = []
    for period, (period_mental_r, period_dif_angle) in periods.items():
        rows.append(
            {
                "trial": trial,
                "alpha": alpha,
                "source_file": str(csv_path),
                "period": period,
                "n_mental_r": int(np.isfinite(period_mental_r).sum()),
                "n_dif_angle": int(np.isfinite(period_dif_angle).sum()),
                "mental_r_mean": finite_or_nan(period_mental_r, "mean"),
                "dif_angle_std": finite_or_nan(period_dif_angle, "std"),
            }
        )
    return rows


def summarize_rows(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["period"]), str(row["alpha"])), []).append(row)

    summary_rows: List[Dict[str, object]] = []
    for (period, alpha), group in sorted(
        grouped.items(),
        key=lambda item: (item[0][0], sort_alpha_key(item[0][1])),
    ):
        for metric in ("mental_r_mean", "dif_angle_std"):
            values = [float(row[metric]) for row in group]
            finite_values = [value for value in values if np.isfinite(value)]
            summary_rows.append(
                {
                    "period": period,
                    "alpha": alpha,
                    "metric": metric,
                    "mean": finite_or_nan(finite_values, "mean"),
                    "sem": sem(finite_values),
                    "n_trials": len(finite_values),
                }
            )
    return summary_rows


def write_csv(rows: List[Dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"No rows to write for {output_path}")

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_metric(
    summary_rows: List[Dict[str, object]],
    metric: str,
    period: str,
    fig_path: Path,
) -> None:
    selected = [
        row
        for row in summary_rows
        if row["metric"] == metric and row["period"] == period
    ]
    selected = sorted(selected, key=lambda row: sort_alpha_key(row["alpha"]))
    if not selected:
        return

    alpha_values = [float(row["alpha"]) for row in selected]
    means = [float(row["mean"]) for row in selected]
    sems = [float(row["sem"]) for row in selected]

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.0, 4.5), constrained_layout=True)
    ax.errorbar(
        alpha_values,
        means,
        yerr=sems,
        marker="o",
        markersize=5,
        linewidth=1.8,
        capsize=4,
        color="#3366aa",
        ecolor="#444444",
        elinewidth=1.1,
    )
    ax.set_xlabel("alpha")
    ax.set_ylabel(METRIC_LABELS[metric])
    ax.set_title(f"{METRIC_LABELS[metric]} ({PERIOD_LABELS[period]})")
    ax.set_xticks(alpha_values)
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)


def plot_all(summary_rows: List[Dict[str, object]], output_dir: Path) -> List[Path]:
    fig_paths: List[Path] = []
    for metric in ("mental_r_mean", "dif_angle_std"):
        for period in ("whole_trial", "last_3_4"):
            fig_path = output_dir / f"{metric}_{period}_by_alpha.png"
            plot_metric(summary_rows, metric, period, fig_path)
            fig_paths.append(fig_path)
    return fig_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze simulated mental_r means and dif_angle standard deviations "
            "by alpha, averaged across trials with SEM."
        )
    )
    parser.add_argument("--input-dir", type=Path, default=SIMULATION_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--trials", nargs="+", default=None, help="optional trial folders, e.g. trial_01 trial_02")
    parser.add_argument("--max-files", type=int, default=None, help="optional limit for quick testing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = simulation_files(args.input_dir, args.trials)
    if args.max_files is not None:
        files = files[: args.max_files]
    if not files:
        raise FileNotFoundError(f"No simulation CSV files found in {args.input_dir}")

    rows: List[Dict[str, object]] = []
    for csv_path in files:
        rows.extend(analyze_file(csv_path))

    summary_rows = summarize_rows(rows)
    per_trial_path = args.output_dir / "order_parameter_per_trial.csv"
    summary_path = args.output_dir / "order_parameter_summary_by_alpha.csv"
    write_csv(rows, per_trial_path)
    write_csv(summary_rows, summary_path)
    fig_paths = plot_all(summary_rows, args.output_dir)

    print(f"Input: {args.input_dir}")
    print(f"Files analyzed: {len(files)}")
    print(f"Saved per-trial metrics: {per_trial_path}")
    print(f"Saved alpha summary: {summary_path}")
    for fig_path in fig_paths:
        print(f"Saved figure: {fig_path}")


if __name__ == "__main__":
    main()
