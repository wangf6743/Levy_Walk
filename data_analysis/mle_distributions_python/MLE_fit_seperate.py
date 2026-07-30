from __future__ import annotations

import csv
import math
import os
from pathlib import Path

import numpy as np
from scipy.io import loadmat, savemat

from mle_source_strict import deterministic_sample, fit_distribution, source_style_steps_from_xy

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib_cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUT_DIR = SCRIPT_DIR.parent / "data_index"
OUT_FILE = OUT_DIR / "mle_wall_margin_5cm_dimension_quarters_fit_results.csv"
FIG_DIR = OUT_DIR / "mle_pattern_figs"
SUMMARY_FILE = OUT_DIR / "mle_wall_margin_5cm_dimension_quarters_tp_percent_summary.csv"
MARGIN_DIMENSION_SUMMARY_FILE = OUT_DIR / "mle_wall_margin_5cm_dimension_quarters_tp_percent_by_dimension.csv"
FITDATA_FILE = OUT_DIR / "FITDATA_quarters.mat"
FITDATA_CSV_FILE = OUT_DIR / "FITDATA_quarters.csv"
FITDATA_SEGMENT_FILE = OUT_DIR / "FITDATA_quarters_segments.csv"
SEGMENT_FITDATA_DIR = OUT_DIR / "fitdata_by_mouse_segment"



DIMENSION = "x"  # Change to "y" to analyze the y dimension instead.
DIMENSIONS = [DIMENSION]
WALL_MARGINS = [5]
COALESCE = True
FITTING = "best"
P_TEST = True
P_VALUE_TESTS = 50
GOF_P_VALUE_THRESHOLD = 0.1
MIN_FITTED_FRACTION = 0.1
RANDOM_SEED = 42
LINGER_RATE_THRESHOLD = 0.05
REMOVE_LINGER_POINTS =  False
REMOVE_WALL_POINTS = True

# Full mouse list for batch runs:
MICE = [
    "dzpm0112201103", #dzp1 

    "dzpm1409201102", # dzp2
    "dzpm1409201103", # dzp3

    
    "vehm0909201102",
    "vehm2206201101",
    "vehm2306201102",
    "vehm2806201101",
    "vehm0212201102", 
]



def load_mouse_track(mouse_name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, np.ndarray]:
    file_path = DATA_DIR / mouse_name / "data_pos_ling_prog.mat"
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    mat = loadmat(file_path)
    data = np.asarray(mat["data_pos_ling_prog"], dtype=float)
    valid = np.isfinite(data[:, 0]) & np.isfinite(data[:, 1])
    data = data[valid]
    times = np.arange(1, len(data) + 1, dtype=float)
    x = data[:, 0]
    y = data[:, 1]
    center = np.array(
        [
            0.5 * (np.max(x) + np.min(x)),
            0.5 * (np.max(y) + np.min(y)),
        ],
        dtype=float,
    )
    home = data[0, :2]
    radius = float(np.linalg.norm(center - home))

    return times, x, y, radius, center


def quarter_track_periods(
    times: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
) -> list[tuple[str, np.ndarray, np.ndarray, np.ndarray]]:
    boundaries = np.linspace(0, len(times), 5, dtype=int)
    return [
        (
            f"quarter_{i + 1}",
            times[boundaries[i] : boundaries[i + 1]],
            x[boundaries[i] : boundaries[i + 1]],
            y[boundaries[i] : boundaries[i + 1]],
        )
        for i in range(4)
    ]


def make_steps(x: np.ndarray, y: np.ndarray, dimension: str) -> np.ndarray:
    steps = source_style_steps_from_xy(
        x=x,
        y=y,
        dimension=dimension,
        coalesce=COALESCE,
    )
    return steps[np.isfinite(steps) & (steps > 0)]


def delete_nearwallpoints(
    path: np.ndarray,
    radius: float,
    center: np.ndarray,
    wall_margin: float,
) -> tuple[np.ndarray, np.ndarray]:
    if len(path) == 0:
        return path, np.array([], dtype=int)

    inner_radius = max(radius - wall_margin, 0.0)
    distance_from_center = np.linalg.norm(path[:, :2] - center, axis=1)
    keep = distance_from_center < inner_radius
    kept_indices = np.where(keep)[0]
    return path[kept_indices], kept_indices + 1


def combine_pathlets(path: np.ndarray, pathlet_no: np.ndarray) -> np.ndarray:
    if len(path) < 2:
        return path

    breaks = np.where(np.diff(pathlet_no) > 1)[0]
    discrete_point = np.r_[breaks, len(path) - 1]
    pathlet_number = len(discrete_point)
    if pathlet_number <= 1:
        return path

    newpath = path.copy()
    index_start: list[int] = []
    for i in range(pathlet_number - 1):
        index_end0 = discrete_point[i]
        index_end1 = discrete_point[i + 1]
        index_start1 = discrete_point[i] + 1
        index_start.append(index_start1)

        pathlet1x = newpath[index_start1 : index_end1 + 1, 0]
        pathlet1y = newpath[index_start1 : index_end1 + 1, 1]
        if len(pathlet1x) == 0:
            continue

        trans_x = pathlet1x[0] - newpath[index_end0, 0]
        trans_y = pathlet1y[0] - newpath[index_end0, 1]
        newpathlet1x = pathlet1x - trans_x
        newpathlet1y = pathlet1y - trans_y

        diffx = 2.0 * (newpathlet1x - newpathlet1x[0])
        newpathlet1x1 = newpathlet1x - diffx
        newpath[index_start1 : index_end1 + 1, :] = np.column_stack((newpathlet1x1, newpathlet1y))

    if index_start:
        keep = np.ones(len(newpath), dtype=bool)
        keep[np.asarray(index_start, dtype=int)] = False
        newpath = newpath[keep]

    return newpath


def remove_wall_and_combine_pathlets(
    x: np.ndarray,
    y: np.ndarray,
    radius: float,
    center: np.ndarray,
    wall_margin: float,
) -> tuple[np.ndarray, np.ndarray]:
    path = np.column_stack((x, y))
    path1, pathlet_no = delete_nearwallpoints(path, radius, center, wall_margin)
    newpath = combine_pathlets(path1, pathlet_no)
    if len(newpath) == 0:
        return np.array([], dtype=float), np.array([], dtype=float)
    return newpath[:, 0], newpath[:, 1]


def remove_lingering_points(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(x) < 2:
        return x[:0], y[:0]

    dx = np.diff(x)
    dy = np.diff(y)
    rate = np.hypot(dx, dy)
    keep = np.where(rate >= LINGER_RATE_THRESHOLD)[0]
    return x[keep], y[keep]


def decades_from_xmin_xmax(xmin: float, xmax: float) -> float:
    if xmin is None or xmax is None:
        return 0.0
    if xmin <= 0 or xmax <= xmin:
        return 0.0
    return math.log10(xmax / xmin)


def fmt(value: object) -> str:
    if value is None:
        return "nan"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(numeric):
        return "nan"
    return f"{numeric:.6g}"


def fitted_fraction(result, n_steps: int) -> float:
    return result.n_fitted / n_steps if n_steps else 0.0


def classify_exponential_or_tp(exp_result, tp_result, n_steps: int) -> str:
    if exp_result.alt is None or tp_result.alt is None:
        return "Unclassified"

    tp_aic = tp_result.aic_weight
    tp_alt_aic = tp_result.alt.aic_weight
    e_aic = exp_result.aic_weight
    e_alt_aic = exp_result.alt.aic_weight
    tp_gof = tp_result.ks_d
    e_gof = exp_result.ks_d
    tp_p = tp_result.p_value
    e_p = exp_result.p_value
    tp_fraction = fitted_fraction(tp_result, n_steps)
    e_fraction = fitted_fraction(exp_result, n_steps)
    mu = tp_result.alpha
    decades = decades_from_xmin_xmax(tp_result.xmin, tp_result.xmax)

    required = [tp_aic, tp_alt_aic, e_aic, e_alt_aic, tp_gof, e_gof, tp_p, e_p, tp_fraction, e_fraction, mu]
    if any(value is None or not math.isfinite(float(value)) for value in required):
        return "Unclassified"

    if tp_aic > tp_alt_aic:
        if e_aic < e_alt_aic or e_gof > tp_gof:
            if (
                tp_fraction >= MIN_FITTED_FRACTION
                and tp_p >= GOF_P_VALUE_THRESHOLD
                and 1.0 < mu <= 3.0
                and decades > 1.5
            ):
                return "TP"
            return "Unclassified"
        return "Unclassified"

    if tp_aic < tp_alt_aic:
        if e_aic > e_alt_aic:
            return "Exponential"
        if e_aic < e_alt_aic:
            if e_gof < tp_gof:
                return "Exponential"
            return "Unclassified"
    return "Unclassified"


def fit_half(steps: np.ndarray):
    exp_result = fit_distribution(
        steps,
        dist="exponential",
        alt_dist="truncated_pareto",
        fitting=FITTING,
        p_test=P_TEST,
        n_tests=P_VALUE_TESTS,
        random_seed=RANDOM_SEED,
    )
    tp_result = fit_distribution(
        steps,
        dist="truncated_pareto",
        alt_dist="exponential",
        fitting=FITTING,
        p_test=P_TEST,
        n_tests=P_VALUE_TESTS,
        random_seed=RANDOM_SEED,
    )
    return exp_result, tp_result, classify_exponential_or_tp(exp_result, tp_result, len(steps))


def model_log_steps_for_observed_ranks(steps: np.ndarray, result) -> np.ndarray:
    desc_steps = np.sort(np.asarray(steps, dtype=float))[::-1]
    log_model = np.full(len(desc_steps), np.nan, dtype=float)

    required = [result.alpha, result.xmin, result.xmax]
    if any(value is None or not math.isfinite(float(value)) for value in required):
        return log_model
    if result.alpha <= 0 or result.xmin <= 0 or result.xmax <= result.xmin:
        return log_model

    in_fit_range = (desc_steps >= result.xmin) & (desc_steps <= result.xmax)
    n_model = int(np.sum(in_fit_range))
    if n_model == 0:
        return log_model

    model_steps = deterministic_sample(
        result.dist,
        n_model,
        alpha=float(result.alpha),
        xmin=float(result.xmin),
        xmax=float(result.xmax),
    )[::-1]
    log_model[in_fit_range] = np.log10(model_steps)
    return log_model


def quarter_fitdata_matrix(steps: np.ndarray, tp_result, exp_result) -> np.ndarray:
    desc_steps = np.sort(np.asarray(steps, dtype=float))[::-1]
    ranks = np.arange(1, len(desc_steps) + 1, dtype=float)
    return np.column_stack(
        (
            np.log10(ranks),
            np.log10(desc_steps),
            model_log_steps_for_observed_ranks(desc_steps, tp_result),
            model_log_steps_for_observed_ranks(desc_steps, exp_result),
        )
    )


def append_fitdata_segment(
    fitdata_by_quarter: dict[str, list[np.ndarray]],
    fitdata_segments: list[dict[str, object]],
    *,
    mouse: str,
    period: str,
    wall_margin: float,
    dimension: str,
    steps: np.ndarray,
    exp_result,
    tp_result,
    label: str,
) -> None:
    segment = quarter_fitdata_matrix(steps, tp_result, exp_result)
    if len(segment) == 0:
        return

    pieces = fitdata_by_quarter.setdefault(period, [])
    start_row = sum(len(piece) for piece in pieces) + 1
    if pieces:
        pieces.append(np.full((1, 4), np.nan, dtype=float))
        start_row += 1
    pieces.append(segment)
    end_row = start_row + len(segment) - 1

    fitdata_segments.append(
        {
            "quarter_variable": period.replace("quarter_", "fitdata_q"),
            "mouse": mouse,
            "period": period,
            "wall_margin": wall_margin,
            "dimension": dimension,
            "classification": label,
            "start_row": start_row,
            "end_row": end_row,
            "n_steps": len(steps),
            "tp_mu": tp_result.alpha,
            "tp_xmin": tp_result.xmin,
            "tp_xmax": tp_result.xmax,
            "exp_lambda": exp_result.alpha,
            "exp_xmin": exp_result.xmin,
            "exp_xmax": exp_result.xmax,
        }
    )


def analysis_fitdata_matrix(steps: np.ndarray, result) -> np.ndarray:
    desc_steps = np.sort(np.asarray(steps, dtype=float))[::-1]
    ranks = np.arange(1, len(desc_steps) + 1, dtype=float)
    log_alternate = np.full(len(desc_steps), np.nan, dtype=float)
    if result.alt is not None:
        log_alternate = model_log_steps_for_observed_ranks(desc_steps, result.alt)
    return np.column_stack(
        (
            ranks,
            np.log10(ranks),
            np.log10(desc_steps),
            model_log_steps_for_observed_ranks(desc_steps, result),
            log_alternate,
        )
    )


def result_value(result, attr: str) -> object:
    if result is None:
        return math.nan
    return getattr(result, attr, math.nan)


def segment_fit_filename(analysis_name: str, wall_margin: float, dimension: str) -> str:
    if len(WALL_MARGINS) == 1 and len(DIMENSIONS) == 1:
        return f"{analysis_name}.csv"
    margin = str(wall_margin).replace(".", "p")
    return f"wall_margin_{margin}_{dimension}_{analysis_name}.csv"


def write_single_segment_fit_csv(
    *,
    mouse: str,
    period: str,
    wall_margin: float,
    dimension: str,
    steps: np.ndarray,
    result,
    analysis_name: str,
) -> Path:
    segment_dir = SEGMENT_FITDATA_DIR / mouse / period
    segment_dir.mkdir(parents=True, exist_ok=True)
    csv_path = segment_dir / segment_fit_filename(analysis_name, wall_margin, dimension)

    fitdata = analysis_fitdata_matrix(steps, result)
    alt = result.alt
    rows = []
    for values in fitdata:
        rows.append(
            {
                "mouse": mouse,
                "segment": period,
                "period": period,
                "wall_margin": wall_margin,
                "dimension": dimension,
                "analysis": analysis_name,
                "best_model": result.name,
                "alternate_model": alt.name if alt is not None else "",
                "n_steps": len(steps),
                "best_n_fitted": result.n_fitted,
                "best_xmin": result.xmin,
                "best_xmax": result.xmax,
                "best_alpha_or_lambda": result.alpha,
                "best_ks_d": result.ks_d,
                "best_log_likelihood": result.log_likelihood,
                "best_p_value": result.p_value,
                "best_aic_weight": result.aic_weight,
                "alternate_n_fitted": result_value(alt, "n_fitted"),
                "alternate_xmin": result_value(alt, "xmin"),
                "alternate_xmax": result_value(alt, "xmax"),
                "alternate_alpha_or_lambda": result_value(alt, "alpha"),
                "alternate_ks_d": result_value(alt, "ks_d"),
                "alternate_log_likelihood": result_value(alt, "log_likelihood"),
                "alternate_p_value": result_value(alt, "p_value"),
                "alternate_aic_weight": result_value(alt, "aic_weight"),
                "rank": values[0],
                "log_rank": values[1],
                "log_observe": values[2],
                "log_bestfit": values[3],
                "log_alternate": values[4],
            }
        )

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return csv_path


def write_segment_fit_csvs(
    *,
    mouse: str,
    period: str,
    wall_margin: float,
    dimension: str,
    steps: np.ndarray,
    exp_result,
    tp_result,
) -> None:
    write_single_segment_fit_csv(
        mouse=mouse,
        period=period,
        wall_margin=wall_margin,
        dimension=dimension,
        steps=steps,
        result=tp_result,
        analysis_name="tp_fit_alt_exp",
    )
    write_single_segment_fit_csv(
        mouse=mouse,
        period=period,
        wall_margin=wall_margin,
        dimension=dimension,
        steps=steps,
        result=exp_result,
        analysis_name="exp_fit_alt_tp",
    )


def result_row(
    mouse: str,
    period: str,
    wall_margin: float,
    dimension: str,
    n_points_before_filter: int,
    n_points_after_wall_filter: int,
    n_points_after_linger_filter: int,
    radius: float,
    steps: np.ndarray,
    exp_result,
    tp_result,
    label: str,
) -> dict[str, object]:
    return {
        "mouse": mouse,
        "period": period,
        "wall_margin": wall_margin,
        "dimension": dimension,
        "coalesce": COALESCE,
        "fitting": FITTING,
        "gof_p_value_threshold": GOF_P_VALUE_THRESHOLD,
        "min_fitted_fraction": MIN_FITTED_FRACTION,
        "arena_radius": radius,
        "n_points_before_filter": n_points_before_filter,
        "n_points_after_linger_filter": n_points_after_linger_filter,
        "n_linger_removed": n_points_before_filter - n_points_after_linger_filter,
        "linger_removed_fraction": (
            (n_points_before_filter - n_points_after_linger_filter) / n_points_before_filter
            if n_points_before_filter
            else math.nan
        ),
        "n_points_after_wall_filter": n_points_after_wall_filter,
        "n_wall_removed": n_points_after_linger_filter - n_points_after_wall_filter,
        "wall_removed_fraction": (
            (n_points_after_linger_filter - n_points_after_wall_filter) / n_points_after_linger_filter
            if n_points_after_linger_filter
            else math.nan
        ),
        "n_steps": len(steps),
        "step_min": float(np.min(steps)) if len(steps) else math.nan,
        "step_median": float(np.median(steps)) if len(steps) else math.nan,
        "step_mean": float(np.mean(steps)) if len(steps) else math.nan,
        "step_max": float(np.max(steps)) if len(steps) else math.nan,
        "exp_n_fitted": exp_result.n_fitted,
        "exp_fitted_fraction": fitted_fraction(exp_result, len(steps)),
        "exp_lambda": exp_result.alpha,
        "exp_xmin": exp_result.xmin,
        "exp_xmax": exp_result.xmax,
        "exp_ks_d": exp_result.ks_d,
        "exp_log_likelihood": exp_result.log_likelihood,
        "exp_p_value": exp_result.p_value,
        "exp_aic_weight": exp_result.aic_weight,
        "exp_alt_tp_aic_weight": exp_result.alt.aic_weight if exp_result.alt else math.nan,
        "tp_n_fitted": tp_result.n_fitted,
        "tp_fitted_fraction": fitted_fraction(tp_result, len(steps)),
        "tp_mu": tp_result.alpha,
        "tp_xmin": tp_result.xmin,
        "tp_xmax": tp_result.xmax,
        "tp_decades": decades_from_xmin_xmax(tp_result.xmin, tp_result.xmax),
        "tp_ks_d": tp_result.ks_d,
        "tp_log_likelihood": tp_result.log_likelihood,
        "tp_p_value": tp_result.p_value,
        "tp_aic_weight": tp_result.aic_weight,
        "tp_alt_exp_aic_weight": tp_result.alt.aic_weight if tp_result.alt else math.nan,
        "better_by_ks": "TP" if tp_result.ks_d < exp_result.ks_d else "Exponential",
        "classification": label,
        "is_tp": label == "TP",
    }


def write_results(rows: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_fitdata_quarters(
    fitdata_by_quarter: dict[str, list[np.ndarray]],
    fitdata_segments: list[dict[str, object]],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mat_data = {
        "fitdata_columns": np.array(
            ["log_rank", "log_observe", "log_bestTP", "log_bestEX"],
            dtype=object,
        )
    }
    for quarter_index in range(1, 5):
        period = f"quarter_{quarter_index}"
        pieces = fitdata_by_quarter.get(period, [])
        if pieces:
            mat_data[f"fitdata_q{quarter_index}"] = np.vstack(pieces)
        else:
            mat_data[f"fitdata_q{quarter_index}"] = np.empty((0, 4), dtype=float)

    savemat(FITDATA_FILE, mat_data)

    csv_rows: list[dict[str, object]] = []
    segment_lookup = {
        (segment["period"], int(segment["start_row"]), int(segment["end_row"])): segment
        for segment in fitdata_segments
    }
    for quarter_index in range(1, 5):
        period = f"quarter_{quarter_index}"
        pieces = fitdata_by_quarter.get(period, [])
        if not pieces:
            continue
        fitdata = np.vstack(pieces)
        for row_index, values in enumerate(fitdata, start=1):
            segment_info = {}
            for (segment_period, start_row, end_row), segment in segment_lookup.items():
                if segment_period == period and start_row <= row_index <= end_row:
                    segment_info = segment
                    break
            csv_rows.append(
                {
                    "quarter": period,
                    "quarter_index": quarter_index,
                    "row_in_quarter": row_index,
                    "mouse": segment_info.get("mouse", ""),
                    "wall_margin": segment_info.get("wall_margin", ""),
                    "dimension": segment_info.get("dimension", ""),
                    "classification": segment_info.get("classification", ""),
                    "log_rank": values[0],
                    "log_observe": values[1],
                    "log_bestTP": values[2],
                    "log_bestEX": values[3],
                }
            )

    if csv_rows:
        with FITDATA_CSV_FILE.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)

    if fitdata_segments:
        with FITDATA_SEGMENT_FILE.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(fitdata_segments[0].keys()))
            writer.writeheader()
            writer.writerows(fitdata_segments)

    print(f"Saved quarter fitdata MAT to: {FITDATA_FILE}")
    print(f"Saved quarter fitdata CSV to: {FITDATA_CSV_FILE}")
    print(f"Saved quarter fitdata segment index to: {FITDATA_SEGMENT_FILE}")


def pattern_for_row(row: dict[str, object]) -> str:
    return "TP" if row["classification"] == "TP" else "Mixed"


def margin_dimension_pattern_counts(rows: list[dict[str, object]]) -> np.ndarray:
    counts = np.zeros((len(WALL_MARGINS), len(DIMENSIONS), 2), dtype=int)
    margin_index = {margin: i for i, margin in enumerate(WALL_MARGINS)}
    dimension_index = {dimension: i for i, dimension in enumerate(DIMENSIONS)}
    pattern_index = {"TP": 0, "Mixed": 1}
    for row in rows:
        margin = int(row["wall_margin"])
        dimension = str(row["dimension"])
        if margin in margin_index and dimension in dimension_index:
            counts[margin_index[margin], dimension_index[dimension], pattern_index[pattern_for_row(row)]] += 1
    return counts


def tp_percent(tp_count: int, total_count: int) -> float:
    return 100.0 * tp_count / total_count if total_count else math.nan


def print_wall_margin_tp_ratio(wall_margin: float, margin_rows: list[dict[str, object]]) -> None:
    print(f"\nFinished wall_margin {wall_margin}: TP ratio by quarter across all mice")
    for period in [f"quarter_{i}" for i in range(1, 5)]:
        period_rows = [row for row in margin_rows if row["period"] == period]
        tp_count = sum(row["classification"] == "TP" for row in period_rows)
        total_count = len(period_rows)
        ratio = tp_count / total_count if total_count else math.nan
        percent = tp_percent(tp_count, total_count)
        print(f"  {period}: {ratio:.4f} ({percent:.2f}%, {tp_count}/{total_count})")


def plot_margin_tp_percent_lines(counts: np.ndarray) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig_path = FIG_DIR / "wall_margin_5cm_dimension_quarters_tp_percent.png"

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    colors = plt.cm.viridis(np.linspace(0, 1, len(DIMENSIONS)))

    for dimension_index, dimension in enumerate(DIMENSIONS):
        dimension_counts = counts[:, dimension_index]
        tp_counts = dimension_counts[:, 0]
        totals = np.sum(dimension_counts, axis=1)
        percentages = np.asarray(
            [tp_percent(int(tp_count), int(total)) for tp_count, total in zip(tp_counts, totals)],
            dtype=float,
        )
        ax.plot(
            WALL_MARGINS,
            percentages,
            marker="o",
            linewidth=1.7,
            color=colors[dimension_index],
            label=dimension,
        )

    ax.set_xticks(WALL_MARGINS)
    ax.set_xlabel("Wall margin", fontname="Times New Roman", fontsize=14)
    ax.set_ylabel("TP percentage (%)", fontname="Times New Roman", fontsize=15)
    ax.set_title("TP Percentage by Dimension", fontname="Times New Roman", fontsize=16)
    ax.set_ylim(-3, 103)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, prop={"family": "Times New Roman", "size": 8}, ncol=2)

    fig.tight_layout()
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)
    return fig_path


def summarize_patterns(rows: list[dict[str, object]]) -> None:
    counts = margin_dimension_pattern_counts(rows)
    fig_path = plot_margin_tp_percent_lines(counts)

    margin_summary_rows = []
    margin_dimension_rows = []
    for margin_i, wall_margin in enumerate(WALL_MARGINS):
        margin_counts = counts[margin_i]
        margin_tp = int(np.sum(margin_counts[:, 0]))
        margin_total = int(np.sum(margin_counts))
        margin_summary_rows.append(
            {
                "wall_margin": wall_margin,
                "tp": margin_tp,
                "total": margin_total,
                "tp_percent": tp_percent(margin_tp, margin_total),
                "figure": str(fig_path),
            }
        )
        for dimension_i, dimension in enumerate(DIMENSIONS):
            dimension_tp = int(margin_counts[dimension_i, 0])
            dimension_mixed = int(margin_counts[dimension_i, 1])
            dimension_total = dimension_tp + dimension_mixed
            margin_dimension_rows.append(
                {
                    "wall_margin": wall_margin,
                    "dimension": dimension,
                    "tp": dimension_tp,
                    "mixed": dimension_mixed,
                    "total": dimension_total,
                    "tp_percent": tp_percent(dimension_tp, dimension_total),
                    "figure": str(fig_path),
                }
            )

    print("\nTP percentage by wall margin")
    for row in margin_summary_rows:
        print(f"  margin {row['wall_margin']}: {row['tp_percent']:.2f}% ({row['tp']}/{row['total']})")
    print(f"  figure = {fig_path}")

    with SUMMARY_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(margin_summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(margin_summary_rows)

    with MARGIN_DIMENSION_SUMMARY_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(margin_dimension_rows[0].keys()))
        writer.writeheader()
        writer.writerows(margin_dimension_rows)

    print(f"Saved margin TP percent summary to: {SUMMARY_FILE}")
    print(f"Saved margin-by-dimension TP percent summary to: {MARGIN_DIMENSION_SUMMARY_FILE}")


def print_period_details(
    period: str,
    n_points_before_filter: int,
    n_points_after_linger_filter: int,
    n_points_after_wall_filter: int,
    steps: np.ndarray,
    exp_result,
    tp_result,
    label: str,
) -> None:
    n_linger_removed = n_points_before_filter - n_points_after_linger_filter
    n_wall_removed = n_points_after_linger_filter - n_points_after_wall_filter
    print(f"  {period}:")
    print(f"    points_before_filter      = {n_points_before_filter}")
    print(f"    points_after_linger_filter = {n_points_after_linger_filter}")
    print(f"    linger_removed            = {n_linger_removed}")
    print(f"    points_after_wall_filter  = {n_points_after_wall_filter}")
    print(f"    wall_removed              = {n_wall_removed}")
    print(f"    steps                     = {len(steps)}")
    print(
        "    step_summary              = "
        f"min {np.min(steps):.6g}, median {np.median(steps):.6g}, "
        f"mean {np.mean(steps):.6g}, max {np.max(steps):.6g}"
    )
    print(
        "    Exponential               = "
        f"lambda {fmt(exp_result.alpha)}, xmin {fmt(exp_result.xmin)}, "
        f"xmax {fmt(exp_result.xmax)}, KS {fmt(exp_result.ks_d)}, "
        f"p {fmt(exp_result.p_value)}, AICw {fmt(exp_result.aic_weight)}"
    )
    print(
        "    TP                        = "
        f"mu {fmt(tp_result.alpha)}, xmin {fmt(tp_result.xmin)}, "
        f"xmax {fmt(tp_result.xmax)}, decades {fmt(decades_from_xmin_xmax(tp_result.xmin, tp_result.xmax))}, "
        f"KS {fmt(tp_result.ks_d)}, p {fmt(tp_result.p_value)}, AICw {fmt(tp_result.aic_weight)}"
    )
    print(f"    classification            = {label}")
    print(f"    is_tp                     = {label == 'TP'}")


def main() -> None:
    rows: list[dict[str, object]] = []
    fitdata_by_quarter: dict[str, list[np.ndarray]] = {}
    fitdata_segments: list[dict[str, object]] = []
    print(f"Data dir: {DATA_DIR}")
    print(f"Output: {OUT_FILE}")
    print(f"Segment fit CSV dir: {SEGMENT_FITDATA_DIR}")
    print(f"Wall margins: {WALL_MARGINS}")
    print(f"Dimensions: {DIMENSIONS}")
    print(f"Coalesce: {COALESCE}, fitting: {FITTING}")
    print(f"GOF p-value threshold: >= {GOF_P_VALUE_THRESHOLD}")
    print(f"Minimum fitted fraction: >= {MIN_FITTED_FRACTION}")
    print(f"Remove lingering points: {REMOVE_LINGER_POINTS}")
    if REMOVE_LINGER_POINTS:
        print(f"Linger rate threshold: {LINGER_RATE_THRESHOLD}")
    print(f"Remove wall points: {REMOVE_WALL_POINTS}")
    print(f"P-test: {P_TEST}, n_tests: {P_VALUE_TESTS}")

    mouse_tracks = []
    for mouse in MICE:
        times, x, y, radius, center = load_mouse_track(mouse)
        mouse_tracks.append((mouse, times, x, y, radius, center))

    for wall_margin in WALL_MARGINS:
        print(f"\nProcessing wall_margin {wall_margin} across all mice...")
        margin_rows: list[dict[str, object]] = []

        for mouse, times, x, y, radius, center in mouse_tracks:
            for period, period_times, period_x, period_y in quarter_track_periods(times, x, y):
                if REMOVE_LINGER_POINTS:
                    linger_x, linger_y = remove_lingering_points(period_x, period_y)
                else:
                    linger_x, linger_y = period_x, period_y

                if REMOVE_WALL_POINTS:
                    fit_x, fit_y = remove_wall_and_combine_pathlets(
                        linger_x,
                        linger_y,
                        radius,
                        center,
                        wall_margin,
                    )
                else:
                    fit_x, fit_y = linger_x, linger_y

                for dimension in DIMENSIONS:
                    steps = make_steps(fit_x, fit_y, dimension)
                    if len(steps) < 2:
                        continue

                    exp_result, tp_result, label = fit_half(steps)
                    row = result_row(
                        mouse,
                        period,
                        wall_margin,
                        dimension,
                        len(period_x),
                        len(fit_x),
                        len(linger_x),
                        radius,
                        steps,
                        exp_result,
                        tp_result,
                        label,
                    )
                    rows.append(row)
                    margin_rows.append(row)
                    append_fitdata_segment(
                        fitdata_by_quarter,
                        fitdata_segments,
                        mouse=mouse,
                        period=period,
                        wall_margin=wall_margin,
                        dimension=dimension,
                        steps=steps,
                        exp_result=exp_result,
                        tp_result=tp_result,
                        label=label,
                    )
                    write_segment_fit_csvs(
                        mouse=mouse,
                        period=period,
                        wall_margin=wall_margin,
                        dimension=dimension,
                        steps=steps,
                        exp_result=exp_result,
                        tp_result=tp_result,
                    )
                    print(
                        f"{mouse}, {period}, wall_margin={wall_margin}, dimension={dimension}, "
                        f"n_steps={len(steps)}, classification={label}, is_tp={label == 'TP'}"
                    )

        print_wall_margin_tp_ratio(wall_margin, margin_rows)

    if not rows:
        raise RuntimeError("No results were produced.")

    write_results(rows)
    print(f"\nSaved {len(rows)} rows to: {OUT_FILE}")
    write_fitdata_quarters(fitdata_by_quarter, fitdata_segments)
    summarize_patterns(rows)


if __name__ == "__main__":
    main()
