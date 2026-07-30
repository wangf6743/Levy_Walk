from __future__ import annotations

import csv
import math
import os
import re
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
SOURCE_DIR = PROJECT_DIR / "data_for_analysis" / "mle_distributions_python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from mle_source_strict import fit_distribution, source_style_steps_from_xy

os.environ.setdefault("MPLCONFIGDIR", str(SCRIPT_DIR / ".matplotlib_cache"))

DATA_DIR = SCRIPT_DIR / "data_simulation" # the folder where the simulation data are stored
OUT_DIR = DATA_DIR / "analysis" / "mle_quarter_model_classification"
OUT_FILE = OUT_DIR / "simulation_model_classification.csv"

DIMENSION = "x"
DIMENSIONS = [DIMENSION]
COALESCE = True
FITTING = "best"
P_TEST = True
P_VALUE_TESTS = 50
GOF_P_VALUE_THRESHOLD = 0.1
MIN_FITTED_FRACTION = 0.1
RANDOM_SEED = 42
MIN_STEPS_FOR_FIT = 50
CIRCLING_LABEL = "circling"


def simulation_files(input_dir: Path) -> list[Path]:
    return sorted(input_dir.glob("trial_*/alpha_*.csv"), key=simulation_sort_key)


def simulation_sort_key(path: Path) -> tuple[int, float]:
    return (trial_number(path.parent.name), alpha_value(path))


def trial_number(trial_name: str) -> int:
    match = re.search(r"(\d+)$", trial_name)
    return int(match.group(1)) if match else -1


def alpha_value(path: Path) -> float:
    text = path.stem.replace("alpha_", "").replace("minus_", "-").replace("p", ".")
    try:
        return float(text)
    except ValueError:
        return math.nan


def load_simulation_track(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    data = np.genfromtxt(path, delimiter=",", names=True, dtype=float)
    if data.size == 0:
        return np.array([], dtype=float), np.array([], dtype=float), np.array([], dtype=float)
    data = np.atleast_1d(data)
    step = np.asarray(data["step"], dtype=float)
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    valid = np.isfinite(step) & np.isfinite(x) & np.isfinite(y)
    return step[valid], x[valid], y[valid]


def split_into_quarters(step: np.ndarray, x: np.ndarray, y: np.ndarray) -> list[tuple[str, np.ndarray, np.ndarray, np.ndarray]]:
    boundaries = np.linspace(0, len(step), 5, dtype=int)
    return [
        (
            f"period_{period_index + 1}",
            step[boundaries[period_index] : boundaries[period_index + 1]],
            x[boundaries[period_index] : boundaries[period_index + 1]],
            y[boundaries[period_index] : boundaries[period_index + 1]],
        )
        for period_index in range(4)
    ]


def make_steps(x: np.ndarray, y: np.ndarray, dimension: str) -> np.ndarray:
    steps = source_style_steps_from_xy(
        x=x,
        y=y,
        dimension=dimension,
        coalesce=COALESCE,
    )
    return steps[np.isfinite(steps) & (steps > 0)]


def decades_from_xmin_xmax(xmin: float, xmax: float) -> float:
    if xmin is None or xmax is None:
        return 0.0
    if xmin <= 0 or xmax <= xmin:
        return 0.0
    return math.log10(xmax / xmin)


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


def fit_models(steps: np.ndarray):
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
    label = classify_exponential_or_tp(exp_result, tp_result, len(steps))
    return exp_result, tp_result, label


def blank_result_row(
    *,
    file_path: Path,
    period: str,
    dimension: str,
    n_points: int,
    n_steps: int,
    classification: str,
    reason: str,
) -> dict[str, object]:
    return {
        "trial": file_path.parent.name,
        "trial_index": trial_number(file_path.parent.name),
        "alpha": alpha_value(file_path),
        "alpha_file": file_path.name,
        "period": period,
        "dimension": dimension,
        "classification": classification,
        "is_tp": False,
        "reason": reason,
        "n_points": n_points,
        "n_steps": n_steps,
        "step_min": math.nan,
        "step_median": math.nan,
        "step_mean": math.nan,
        "step_max": math.nan,
        "exp_lambda": math.nan,
        "exp_xmin": math.nan,
        "exp_xmax": math.nan,
        "exp_n_fitted": math.nan,
        "exp_fitted_fraction": math.nan,
        "exp_ks_d": math.nan,
        "exp_p_value": math.nan,
        "exp_aic_weight": math.nan,
        "tp_mu": math.nan,
        "tp_xmin": math.nan,
        "tp_xmax": math.nan,
        "tp_n_fitted": math.nan,
        "tp_fitted_fraction": math.nan,
        "tp_decades": math.nan,
        "tp_ks_d": math.nan,
        "tp_p_value": math.nan,
        "tp_aic_weight": math.nan,
    }


def result_row(
    *,
    file_path: Path,
    period: str,
    dimension: str,
    n_points: int,
    steps: np.ndarray,
    exp_result,
    tp_result,
    classification: str,
) -> dict[str, object]:
    return {
        "trial": file_path.parent.name,
        "trial_index": trial_number(file_path.parent.name),
        "alpha": alpha_value(file_path),
        "alpha_file": file_path.name,
        "period": period,
        "dimension": dimension,
        "classification": classification,
        "is_tp": classification == "TP",
        "reason": "fit_ok",
        "n_points": n_points,
        "n_steps": len(steps),
        "step_min": float(np.min(steps)) if len(steps) else math.nan,
        "step_median": float(np.median(steps)) if len(steps) else math.nan,
        "step_mean": float(np.mean(steps)) if len(steps) else math.nan,
        "step_max": float(np.max(steps)) if len(steps) else math.nan,
        "exp_lambda": exp_result.alpha,
        "exp_xmin": exp_result.xmin,
        "exp_xmax": exp_result.xmax,
        "exp_n_fitted": exp_result.n_fitted,
        "exp_fitted_fraction": fitted_fraction(exp_result, len(steps)),
        "exp_ks_d": exp_result.ks_d,
        "exp_p_value": exp_result.p_value,
        "exp_aic_weight": exp_result.aic_weight,
        "tp_mu": tp_result.alpha if classification == "TP" else math.nan,
        "tp_xmin": tp_result.xmin,
        "tp_xmax": tp_result.xmax,
        "tp_n_fitted": tp_result.n_fitted,
        "tp_fitted_fraction": fitted_fraction(tp_result, len(steps)),
        "tp_decades": decades_from_xmin_xmax(tp_result.xmin, tp_result.xmax),
        "tp_ks_d": tp_result.ks_d,
        "tp_p_value": tp_result.p_value,
        "tp_aic_weight": tp_result.aic_weight,
    }


def write_results(rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError("No rows were produced.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with OUT_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    print(f"Input simulation dir: {DATA_DIR}")
    print(f"Output CSV: {OUT_FILE}")
    print(f"Dimensions: {DIMENSIONS}")
    print(f"Coalesce: {COALESCE}, fitting: {FITTING}")
    print(f"P-test: {P_TEST}, n_tests: {P_VALUE_TESTS}")

    files = simulation_files(DATA_DIR)
    if not files:
        raise FileNotFoundError(f"No simulation CSV files found in {DATA_DIR}/trial_*/alpha_*.csv")

    rows: list[dict[str, object]] = []
    for file_index, file_path in enumerate(files, start=1):
        step, x, y = load_simulation_track(file_path)
        print(f"[{file_index}/{len(files)}] {file_path.parent.name}/{file_path.name}")
        for period, period_step, period_x, period_y in split_into_quarters(step, x, y):
            for dimension in DIMENSIONS:
                steps = make_steps(period_x, period_y, dimension)
                if len(steps) < MIN_STEPS_FOR_FIT:
                    rows.append(
                        blank_result_row(
                            file_path=file_path,
                            period=period,
                            dimension=dimension,
                            n_points=len(period_x),
                            n_steps=len(steps),
                            classification=CIRCLING_LABEL,
                            reason="not_enough_fit_steps",
                        )
                    )
                    continue

                try:
                    exp_result, tp_result, classification = fit_models(steps)
                    rows.append(
                        result_row(
                            file_path=file_path,
                            period=period,
                            dimension=dimension,
                            n_points=len(period_x),
                            steps=steps,
                            exp_result=exp_result,
                            tp_result=tp_result,
                            classification=classification,
                        )
                    )
                except Exception as exc:
                    rows.append(
                        blank_result_row(
                            file_path=file_path,
                            period=period,
                            dimension=dimension,
                            n_points=len(period_x),
                            n_steps=len(steps),
                            classification=CIRCLING_LABEL,
                            reason=f"fit_failed:{type(exc).__name__}",
                        )
                    )

    write_results(rows)
    print(f"\nSaved {len(rows)} rows to: {OUT_FILE}")

    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["classification"])] = counts.get(str(row["classification"]), 0) + 1
    print("Classification counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
