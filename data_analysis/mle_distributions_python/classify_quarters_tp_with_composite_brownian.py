# module load R/4.5 && /u/fwang/levy_project/levy/bin/python /u/fwang/levy_project/data_for_analysis/mle_distributions_python/classify_quarters_tp_with_composite_brownian.py --rscript "$(command -v Rscript)"

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import data_for_analysis.mle_distributions_python.MLE_fit_seperate as quarters
from composite_brownian_r import fit_composite_brownian_r

# module load R/4.5 && /usr/bin/python3.11 /u/fwang/levy_project/data_for_analysis/mle_distributions_python/classify_quarters_tp_with_composite_brownian.py --rscript "$(command -v Rscript)"

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = SCRIPT_DIR.parent / "data_index"
SUMMARY_FILE = DEFAULT_OUT_DIR / "mle_wall_margin_5cm_dimension_quarters_tp_composite_brownian_best_models.csv"
ALL_FITS_FILE = DEFAULT_OUT_DIR / "mle_wall_margin_5cm_dimension_quarters_tp_composite_brownian_all_fits.csv"
STEPS_DIR = DEFAULT_OUT_DIR / "mle_wall_margin_5cm_dimension_quarters_tp_steps_for_composite_brownian"


def fmt(value: object) -> str:
    if value is None:
        return "nan"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(numeric):
        return "nan"
    return f"{numeric:.8g}"


def clean_name(value: object) -> str:
    return str(value).replace("/", "_").replace(" ", "_")


def fitted_steps_for_tp(steps: np.ndarray, tp_result) -> np.ndarray:
    if tp_result.xmin is None or tp_result.xmax is None:
        return np.array([], dtype=float)
    keep = (steps >= tp_result.xmin) & (steps <= tp_result.xmax)
    return steps[keep]


def write_steps(path: Path, steps: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step_length"])
        for value in steps:
            writer.writerow([fmt(value)])


def cb_params_for_row(fit) -> dict[str, object]:
    return {
        "cb_lambda": fit.lambda_,
        "cb_mu": fit.mu,
        "cb_p1": fit.p1,
        "cb_p2": fit.p2,
        "cb_p3": fit.p3,
        "cb_p4": fit.p4,
        "cb_lb1": fit.lb1,
        "cb_lb2": fit.lb2,
        "cb_lb3": fit.lb3,
        "cb_lb4": fit.lb4,
    }


def cb_model_metrics_for_row(fits) -> dict[str, object]:
    row: dict[str, object] = {}
    for fit in fits:
        prefix = fit.model
        row[f"{prefix}_log_likelihood"] = fit.log_likelihood
        row[f"{prefix}_aic"] = fit.aic
        row[f"{prefix}_aic_weight"] = fit.aic_weight
    return row


def base_row(
    mouse: str,
    period: str,
    wall_margin: float,
    dimension: str,
    steps: np.ndarray,
    tp_steps: np.ndarray,
    exp_result,
    tp_result,
) -> dict[str, object]:
    return {
        "mouse": mouse,
        "period": period,
        "wall_margin": wall_margin,
        "dimension": dimension,
        "source_classification": "TP",
        "n_steps": len(steps),
        "n_tp_fitted_steps": len(tp_steps),
        "tp_fitted_fraction": quarters.fitted_fraction(tp_result, len(steps)),
        "tp_mu": tp_result.alpha,
        "tp_xmin": tp_result.xmin,
        "tp_xmax": tp_result.xmax,
        "cb_input_xmin": tp_result.xmin,
        "cb_input_xmax": tp_result.xmax,
        "tp_decades": quarters.decades_from_xmin_xmax(tp_result.xmin, tp_result.xmax),
        "tp_ks_d": tp_result.ks_d,
        "tp_p_value": tp_result.p_value,
        "tp_aic_weight": tp_result.aic_weight,
        "tp_alt_exp_aic_weight": tp_result.alt.aic_weight if tp_result.alt else math.nan,
        "exp_ks_d": exp_result.ks_d,
        "exp_p_value": exp_result.p_value,
        "exp_aic_weight": exp_result.aic_weight,
        "exp_alt_tp_aic_weight": exp_result.alt.aic_weight if exp_result.alt else math.nan,
    }


def fit_tp_datasets_with_cb(rscript: str, start_profile: str, save_steps: bool) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    summary_rows: list[dict[str, object]] = []
    all_fit_rows: list[dict[str, object]] = []

    mouse_tracks = []
    for mouse in quarters.MICE:
        times, x, y, radius, center = quarters.load_mouse_track(mouse)
        mouse_tracks.append((mouse, times, x, y, radius, center))

    for wall_margin in quarters.WALL_MARGINS:
        print(f"\nProcessing wall_margin {wall_margin}...")
        for mouse, times, x, y, radius, center in mouse_tracks:
            for period, _period_times, period_x, period_y in quarters.quarter_track_periods(times, x, y):
                if quarters.REMOVE_LINGER_POINTS:
                    linger_x, linger_y = quarters.remove_lingering_points(period_x, period_y)
                else:
                    linger_x, linger_y = period_x, period_y

                if quarters.REMOVE_WALL_POINTS:
                    fit_x, fit_y = quarters.remove_wall_and_combine_pathlets(
                        linger_x,
                        linger_y,
                        radius,
                        center,
                        wall_margin,
                    )
                else:
                    fit_x, fit_y = linger_x, linger_y

                for dimension in quarters.DIMENSIONS:
                    steps = quarters.make_steps(fit_x, fit_y, dimension)
                    if len(steps) < 2:
                        continue

                    exp_result, tp_result, label = quarters.fit_half(steps)
                    print(
                        f"{mouse}, {period}, dimension={dimension}, n_steps={len(steps)}, "
                        f"quarter_classification={label}"
                    )
                    if label != "TP":
                        continue

                    tp_steps = fitted_steps_for_tp(steps, tp_result)
                    if len(tp_steps) < 2:
                        print(f"  skipped composite Brownian fit: only {len(tp_steps)} TP fitted steps")
                        continue

                    step_file = ""
                    if save_steps:
                        step_path = STEPS_DIR / (
                            f"{clean_name(mouse)}_{clean_name(period)}_"
                            f"wall_margin_{clean_name(wall_margin)}_"
                            f"dimension_{clean_name(dimension)}_tp_steps.csv"
                        )
                        write_steps(step_path, tp_steps)
                        step_file = str(step_path)

                    cb_fits = fit_composite_brownian_r(
                        tp_steps,
                        rscript=rscript,
                        start_profile=start_profile,
                    )
                    best_fit = min(cb_fits, key=lambda fit: fit.aic)
                    print(
                        f"  TP fitted steps={len(tp_steps)}, "
                        f"best_cb_model={best_fit.model}, AIC={best_fit.aic:.6g}, "
                        f"AICw={best_fit.aic_weight:.6g}"
                    )

                    common = base_row(
                        mouse,
                        period,
                        wall_margin,
                        dimension,
                        steps,
                        tp_steps,
                        exp_result,
                        tp_result,
                    )
                    common["tp_steps_file"] = step_file

                    summary_row = dict(common)
                    summary_row.update(
                    {
                        "best_cb_model_by_aic": best_fit.model,
                        "best_cb_aic": best_fit.aic,
                        "best_cb_aic_weight": best_fit.aic_weight,
                        "best_cb_log_likelihood": best_fit.log_likelihood,
                    }
                )
                    summary_row.update(cb_model_metrics_for_row(cb_fits))
                    summary_row.update(cb_params_for_row(best_fit))
                    summary_rows.append(summary_row)

                    for fit in cb_fits:
                        fit_row = dict(common)
                        fit_row.update(
                        {
                            "cb_model": fit.model,
                            "cb_n_components": fit.n_components,
                            "cb_n_params": fit.n_params,
                            "cb_n_steps": fit.n_steps,
                            "cb_xmin": fit.xmin,
                            "cb_xmax": fit.xmax,
                            "cb_log_likelihood": fit.log_likelihood,
                            "cb_aic": fit.aic,
                            "cb_aic_weight": fit.aic_weight,
                            "is_best_cb_model": fit.model == best_fit.model,
                        }
                    )
                        fit_row.update(cb_params_for_row(fit))
                        all_fit_rows.append(fit_row)

    return summary_rows, all_fit_rows


def write_dict_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError("No rows were produced.")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Use quarter-track MLE TP classification, then fit TP fitted step lengths "
            "with composite_brownian_r.py and classify by AIC."
        )
    )
    parser.add_argument("--rscript", default=os.environ.get("RSCRIPT", "Rscript"), help="Rscript executable")
    parser.add_argument(
        "--start-profile",
        choices=["gps", "mussel"],
        default="gps",
        help="starting values profile used by composite_brownian_r.py",
    )
    parser.add_argument("--summary-file", type=Path, default=SUMMARY_FILE)
    parser.add_argument("--all-fits-file", type=Path, default=ALL_FITS_FILE)
    parser.add_argument(
        "--no-save-steps",
        action="store_true",
        help="do not save the TP fitted step lengths passed to composite_brownian_r.py",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary_rows, all_fit_rows = fit_tp_datasets_with_cb(
        rscript=args.rscript,
        start_profile=args.start_profile,
        save_steps=not args.no_save_steps,
    )
    write_dict_rows(args.summary_file, summary_rows)
    write_dict_rows(args.all_fits_file, all_fit_rows)
    print(f"\nSaved best-model summary: {args.summary_file}")
    print(f"Saved all composite Brownian fits: {args.all_fits_file}")
    if not args.no_save_steps:
        print(f"Saved TP fitted step-length CSV files in: {STEPS_DIR}")


if __name__ == "__main__":
    main()
