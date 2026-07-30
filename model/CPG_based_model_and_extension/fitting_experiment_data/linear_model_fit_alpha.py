# Full-track alpha vs turning-angle SD segmented regression via Rscript.
# Python computes full-track dif_angle SD; R segmented fits 0..KMAX breakpoints.

import csv
import math
import multiprocessing as mp
import os
import re
import shlex
import subprocess
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(SCRIPT_DIR / ".matplotlib_cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for font_path in [
    Path.home() / ".local" / "share" / "fonts" / "Arial.TTF",
    Path("/u/fwang/.local/share/fonts/Arial.TTF"),
]:
    if font_path.exists():
        font_manager.fontManager.addfont(str(font_path))
        break

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "mathtext.fontset": "custom",
    "mathtext.rm": "Arial",
    "mathtext.it": "Arial:italic",
    "mathtext.bf": "Arial:bold",
    "mathtext.sf": "Arial",
    "mathtext.cal": "Arial",
})

DATA_DIR = SCRIPT_DIR / "data_simulation0.02"
OUT_DIR = DATA_DIR / "analysis" / "r_segmented_full_track_last50_two_step"
FIT_FIG_DIR = OUT_DIR / "fit_by_breakpoint_count"
PER_TRIAL_CSV = OUT_DIR / "full_track_two_step_dif_angle_sd_by_trial_alpha_last50.csv"
R_INPUT_CSV = OUT_DIR / "r_segmented_two_step_input_full_track_last50.csv"
FIT_CSV = OUT_DIR / "r_segmented_two_step_metrics_0_to_5_breakpoints.csv"
PRED_CSV = OUT_DIR / "r_segmented_two_step_predictions_0_to_5_breakpoints.csv"
SLOPE_CSV = OUT_DIR / "r_segmented_two_step_slopes_0_to_5_breakpoints.csv"
R_SCRIPT_PATH = OUT_DIR / "fit_r_segmented_two_step_0_to_5_breakpoints.R"
BIC_FIG_PNG = OUT_DIR / "r_segmented_bic_by_breakpoint_count.png"
BIC_FIG_SVG = OUT_DIR / "r_segmented_bic_by_breakpoint_count.svg"
ADJ_R2_FIG_PNG = OUT_DIR / "r_segmented_adjusted_r2_by_breakpoint_count.png"
ADJ_R2_FIG_SVG = OUT_DIR / "r_segmented_adjusted_r2_by_breakpoint_count.svg"

MIN_TRIAL_INDEX = 1
MAX_TRIAL_INDEX = 50
KMAX_BREAKPOINTS = int(os.environ.get("KMAX_BREAKPOINTS", 5))
N_PROCESSES = int(os.environ.get("N_PROCESSES", max(1, min(mp.cpu_count(), 16))))
R_MODULE = os.environ.get("R_MODULE", "R/4.4")
RSCRIPT = os.environ.get("RSCRIPT", "Rscript")
R_LIBS_USER = Path(os.environ.get("R_LIBS_USER", SCRIPT_DIR / "R_libs" / "R_4.4"))
os.environ.setdefault("R_LIBS_USER", str(R_LIBS_USER))

R_SEGMENTED_SCRIPT = r'''
args <- commandArgs(trailingOnly = TRUE)
input_csv <- args[[1]]
fit_csv <- args[[2]]
pred_csv <- args[[3]]
slope_csv <- args[[4]]
kmax <- as.integer(args[[5]])

if (!requireNamespace("segmented", quietly = TRUE)) {
  stop("R package 'segmented' is not installed. Run install.packages('segmented') first.", call. = FALSE)
}

d <- read.csv(input_csv)
d <- d[is.finite(d$x) & is.finite(d$y), ]
d <- d[order(d$x), ]
x_grid <- seq(min(d$x), max(d$x), length.out = 400)

score_model <- function(y, y_pred, n_breakpoints) {
  n <- length(y)
  n_segments <- n_breakpoints + 1
  n_parameters <- n_segments + 1 + n_breakpoints
  ss_res <- sum((y - y_pred) ^ 2)
  ss_tot <- sum((y - mean(y)) ^ 2)
  r2 <- if (ss_tot > 0) 1 - ss_res / ss_tot else NA_real_
  r <- if (sd(y_pred) > 0) as.numeric(cor(y, y_pred)) else NA_real_
  adjusted_r2 <- if (n > n_parameters + 1) 1 - (1 - r2) * (n - 1) / (n - n_parameters - 1) else NA_real_
  aic <- if (ss_res > 0) n * log(ss_res / n) + 2 * n_parameters else NA_real_
  bic <- if (ss_res > 0) n * log(ss_res / n) + n_parameters * log(n) else NA_real_
  list(r = r, r2 = r2, adjusted_r2 = adjusted_r2, aic = aic, bic = bic, ss_res = ss_res)
}

extract_breakpoints <- function(model) {
  psi <- model$psi
  if (is.null(psi)) return(numeric(0))
  psi <- as.data.frame(psi)
  est_col <- grep("^Est", names(psi), value = TRUE)[1]
  if (is.na(est_col)) return(numeric(0))
  sort(as.numeric(psi[[est_col]]))
}

segment_slopes <- function(model, k, breaks) {
  rows <- list()
  for (i in seq_len(length(breaks) - 1)) {
    x0 <- breaks[i]
    x1 <- breaks[i + 1]
    yp <- as.numeric(predict(model, newdata = data.frame(x = c(x0, x1))))
    segment_slope <- (yp[2] - yp[1]) / (x1 - x0)
    segment_intercept <- yp[1] - segment_slope * x0
    rows[[length(rows) + 1]] <- data.frame(
      requested_breakpoints = k,
      segment_index = i,
      x_start = x0,
      x_end = x1,
      slope = segment_slope,
      intercept = segment_intercept
    )
  }
  do.call(rbind, rows)
}

fit_k <- function(k) {
  base <- lm(y ~ x, data = d)
  if (k == 0) {
    model <- base
    internal <- numeric(0)
  } else {
    psi0 <- as.numeric(quantile(d$x, probs = seq(1 / (k + 1), k / (k + 1), length.out = k), type = 7))
    model <- segmented::segmented(
      base,
      seg.Z = ~ x,
      psi = list(x = psi0),
      control = segmented::seg.control(display = FALSE, n.boot = 0)
    )
    internal <- extract_breakpoints(model)
  }

  y_pred <- as.numeric(predict(model, newdata = d))
  grid_pred <- as.numeric(predict(model, newdata = data.frame(x = x_grid)))
  scores <- score_model(d$y, y_pred, length(internal))
  breaks <- c(min(d$x), internal, max(d$x))

  list(
    metrics = data.frame(
      requested_breakpoints = k,
      n_breakpoints = length(internal),
      n_segments = length(internal) + 1,
      r = scores$r,
      r2 = scores$r2,
      adjusted_r2 = scores$adjusted_r2,
      aic = scores$aic,
      bic = scores$bic,
      ss_res = scores$ss_res,
      breaks = paste(format(breaks, digits = 10), collapse = ";"),
      internal_breakpoints = paste(format(internal, digits = 10), collapse = ";"),
      status = "ok",
      stringsAsFactors = FALSE
    ),
    pred = data.frame(requested_breakpoints = k, x = x_grid, y_pred = grid_pred),
    slopes = segment_slopes(model, k, breaks)
  )
}

empty_metric <- function(k, message) {
  data.frame(
    requested_breakpoints = k,
    n_breakpoints = NA_integer_,
    n_segments = NA_integer_,
    r = NA_real_,
    r2 = NA_real_,
    adjusted_r2 = NA_real_,
    aic = NA_real_,
    bic = NA_real_,
    ss_res = NA_real_,
    breaks = "",
    internal_breakpoints = "",
    status = message,
    stringsAsFactors = FALSE
  )
}

metric_rows <- list()
pred_rows <- list()
slope_rows <- list()
for (k in 0:kmax) {
  fitted <- tryCatch(fit_k(k), error = function(e) e)
  if (inherits(fitted, "error")) {
    metric_rows[[length(metric_rows) + 1]] <- empty_metric(k, conditionMessage(fitted))
  } else {
    metric_rows[[length(metric_rows) + 1]] <- fitted$metrics
    pred_rows[[length(pred_rows) + 1]] <- fitted$pred
    slope_rows[[length(slope_rows) + 1]] <- fitted$slopes
  }
}

write.csv(do.call(rbind, metric_rows), fit_csv, row.names = FALSE)
if (length(pred_rows) > 0) {
  write.csv(do.call(rbind, pred_rows), pred_csv, row.names = FALSE)
} else {
  write.csv(data.frame(requested_breakpoints = integer(), x = numeric(), y_pred = numeric()), pred_csv, row.names = FALSE)
}
if (length(slope_rows) > 0) {
  write.csv(do.call(rbind, slope_rows), slope_csv, row.names = FALSE)
} else {
  write.csv(data.frame(requested_breakpoints = integer(), segment_index = integer(), x_start = numeric(), x_end = numeric(), slope = numeric(), intercept = numeric()), slope_csv, row.names = FALSE)
}
'''


def trial_number(trial_name):
    match = re.search(r"(\d+)$", trial_name)
    return int(match.group(1)) if match else -1


def alpha_value(path):
    text = path.stem.replace("alpha_", "").replace("minus_", "-").replace("p", ".")
    try:
        return float(text)
    except ValueError:
        return math.nan


def alpha_label(alpha):
    return "alpha_{:g}".format(alpha)


def finite(values):
    values = np.asarray(values, dtype=float)
    return values[np.isfinite(values)]


def simulation_files():
    files = [
        path
        for path in DATA_DIR.glob("trial_*/alpha_*.csv")
        if MIN_TRIAL_INDEX <= trial_number(path.parent.name) <= MAX_TRIAL_INDEX
    ]
    return sorted(files, key=lambda path: (trial_number(path.parent.name), alpha_value(path)))


def wrap_to_pi(angle):
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def two_step_dif_angle(path):
    path = np.asarray(path, dtype=float)
    path = path[np.all(np.isfinite(path[:, :2]), axis=1)]
    path = path[::2, :2]
    if len(path) < 3:
        return np.asarray([], dtype=float)
    delta = np.diff(path, axis=0)
    step_angle = np.arctan2(delta[:, 1], delta[:, 0])
    return wrap_to_pi(np.diff(step_angle))


def file_row(file_path):
    path = np.loadtxt(file_path, delimiter=",", skiprows=1, usecols=(1, 2), dtype=float)
    path = np.atleast_2d(path)
    dif_angle = finite(two_step_dif_angle(path))
    dif_angle_sd = float(np.nanstd(dif_angle, ddof=1)) if len(dif_angle) > 1 else np.nan
    alpha = alpha_value(file_path)
    trial = file_path.parent.name

    return {
        "trial": trial,
        "trial_index": trial_number(trial),
        "alpha": alpha,
        "alpha_label": alpha_label(alpha),
        "alpha_file": file_path.name,
        "n_dif_angles": len(dif_angle),
        "dif_angle_sd": dif_angle_sd,
    }


def compute_rows(files):
    if N_PROCESSES == 1:
        rows = [file_row(file_path) for file_path in files]
    else:
        with mp.Pool(processes=N_PROCESSES) as pool:
            rows = list(pool.imap_unordered(file_row, files, chunksize=10))
    return sorted(rows, key=lambda row: (int(row["trial_index"]), float(row["alpha"])))


def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_dicts(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def alpha_sd_arrays(rows):
    x = np.asarray([float(row["alpha"]) for row in rows], dtype=float)
    y = np.asarray([float(row["dif_angle_sd"]) for row in rows], dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    return x[mask], y[mask]


def write_r_input(x, y):
    write_csv(
        R_INPUT_CSV,
        [{"x": float(xi), "y": float(yi)} for xi, yi in zip(x, y)],
        fieldnames=["x", "y"],
    )


def run_rscript_segmented():
    R_SCRIPT_PATH.write_text(R_SEGMENTED_SCRIPT)
    R_LIBS_USER.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["R_LIBS_USER"] = str(R_LIBS_USER)
    r_args = " ".join(shlex.quote(str(value)) for value in [R_SCRIPT_PATH, R_INPUT_CSV, FIT_CSV, PRED_CSV, SLOPE_CSV, KMAX_BREAKPOINTS])
    commands = []
    if R_MODULE:
        commands.append("module load %s" % shlex.quote(R_MODULE))
    commands.append("%s %s" % (shlex.quote(RSCRIPT), r_args))
    subprocess.run(["bash", "-lc", " && ".join(commands)], check=True, env=env)


def row_float(row, key):
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return np.nan


def plot_fit_by_breakpoint(rows):
    x, y = alpha_sd_arrays(rows)
    pred_rows = read_csv_dicts(PRED_CSV)
    fit_rows = read_csv_dicts(FIT_CSV)
    FIT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    paths = []

    for fit_row in fit_rows:
        k = int(float(fit_row["requested_breakpoints"]))
        status = fit_row.get("status", "")
        if status != "ok":
            continue
        pred = [row for row in pred_rows if int(float(row["requested_breakpoints"])) == k]
        if not pred:
            continue
        x_grid = np.asarray([float(row["x"]) for row in pred], dtype=float)
        y_grid = np.asarray([float(row["y_pred"]) for row in pred], dtype=float)

        fig, ax = plt.subplots(figsize=(2.2, 2))
        ax.scatter(x, y, s=2, color="0.65", alpha=1.0, linewidths=0, zorder=1)
        ax.plot(x_grid, y_grid, color="#7B2CBF", linewidth=1.8, zorder=3)

        internal = str(fit_row.get("internal_breakpoints", "")).strip()
        if internal:
            breakpoints = [float(knot) for knot in internal.split(";") if knot.strip()]
            if breakpoints:
                ax.scatter(
                    breakpoints,
                    np.interp(breakpoints, x_grid, y_grid),
                    s=14,
                    color="black",
                    marker="s",
                    linewidths=0,
                    zorder=4,
                )

        ax.set_xlabel(r"$\alpha$", fontsize=10)
        ax.set_ylabel(r"S.D. of $\Delta\theta_t$", fontsize=10)
        ax.tick_params(axis="both", labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlim(float(np.min(x)), float(np.max(x)))
        ax.text(
            0.04,
            0.06,
            ("Adjusted " + chr(36) + "R^2" + chr(36) + " = %.3f") % row_float(fit_row, "adjusted_r2"),
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8,
        )
        fig.tight_layout()
        png_path = FIT_FIG_DIR / ("fit_%d_breakpoints.png" % k)
        svg_path = FIT_FIG_DIR / ("fit_%d_breakpoints.svg" % k)
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        fig.savefig(svg_path, bbox_inches="tight")
        plt.close(fig)
        paths.extend([png_path, svg_path])
    return paths


def plot_bic_line():
    fit_rows = [row for row in read_csv_dicts(FIT_CSV) if row.get("status") == "ok"]
    x = np.asarray([int(float(row["requested_breakpoints"])) for row in fit_rows], dtype=int)
    y = np.asarray([row_float(row, "bic") for row in fit_rows], dtype=float)
    mask = np.isfinite(y)
    x = x[mask]
    y = y[mask]

    fig, ax = plt.subplots(figsize=(2.2, 1.7))
    ax.plot(x, y, color="black", linewidth=1.3, marker="o", markersize=3)
    ax.set_xlabel("Number of breakpoints", fontsize=10)
    ax.set_ylabel("BIC", fontsize=10)
    ax.set_xticks(np.arange(0, KMAX_BREAKPOINTS + 1, 1))
    ax.tick_params(axis="both", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(BIC_FIG_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(BIC_FIG_SVG, bbox_inches="tight")
    plt.close(fig)


def plot_adjusted_r2_line():
    fit_rows = [row for row in read_csv_dicts(FIT_CSV) if row.get("status") == "ok"]
    x = np.asarray([int(float(row["requested_breakpoints"])) for row in fit_rows], dtype=int)
    y = np.asarray([row_float(row, "adjusted_r2") for row in fit_rows], dtype=float)
    mask = np.isfinite(y)
    x = x[mask]
    y = y[mask]

    fig, ax = plt.subplots(figsize=(2.2, 1.7))
    ax.plot(x, y, color="black", linewidth=1.3, marker="o", markersize=3)
    ax.set_xlabel("Number of breakpoints", fontsize=10)
    ax.set_ylabel("Adjusted " + chr(36) + "R^2" + chr(36), fontsize=10)
    ax.set_xticks(np.arange(0, KMAX_BREAKPOINTS + 1, 1))
    ax.tick_params(axis="both", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(ADJ_R2_FIG_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(ADJ_R2_FIG_SVG, bbox_inches="tight")
    plt.close(fig)


def print_fit_metrics():
    rows = read_csv_dicts(FIT_CSV)
    print("\nR segmented fit metrics")
    print("%12s %10s %9s %9s %12s %12s %12s %s" % (
        "requested", "estimated", "r", "r2", "adj_r2", "aic", "bic", "breakpoints"
    ))
    for row in rows:
        if row.get("status") != "ok":
            print("%12s %10s %9s %9s %12s %12s %12s %s" % (
                row.get("requested_breakpoints", ""), "failed", "NA", "NA", "NA", "NA", "NA", row.get("status", "")
            ))
            continue
        print("%12s %10s %9.4f %9.4f %12.4f %12.2f %12.2f %s" % (
            row["requested_breakpoints"],
            row["n_breakpoints"],
            row_float(row, "r"),
            row_float(row, "r2"),
            row_float(row, "adjusted_r2"),
            row_float(row, "aic"),
            row_float(row, "bic"),
            row.get("internal_breakpoints", ""),
        ))


def print_slope_metrics():
    rows = read_csv_dicts(SLOPE_CSV)
    print("\nSegment slopes")
    print("%12s %8s %10s %10s %12s %12s" % (
        "breakpoints", "segment", "x_start", "x_end", "slope", "intercept"
    ))
    for row in rows:
        print("%12s %8s %10.4f %10.4f %12.6f %12.6f" % (
            row["requested_breakpoints"],
            row["segment_index"],
            row_float(row, "x_start"),
            row_float(row, "x_end"),
            row_float(row, "slope"),
            row_float(row, "intercept"),
        ))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = simulation_files()
    if not files:
        raise FileNotFoundError("No simulation files found in %s/trial_51..trial_100/alpha_*.csv" % DATA_DIR)

    print("Computing full-track two-step dif_angle SD from %d CSV files with %d processes" % (len(files), N_PROCESSES))
    rows = compute_rows(files)
    write_csv(PER_TRIAL_CSV, rows)

    x, y = alpha_sd_arrays(rows)
    write_r_input(x, y)

    print("Running Rscript segmented fits for 0..%d breakpoints" % KMAX_BREAKPOINTS)
    run_rscript_segmented()
    fit_fig_paths = plot_fit_by_breakpoint(rows)
    plot_bic_line()
    plot_adjusted_r2_line()
    print_fit_metrics()
    print_slope_metrics()

    print("\nSaved per-trial alpha SD CSV: %s" % PER_TRIAL_CSV)
    print("Saved R input CSV: %s" % R_INPUT_CSV)
    print("Saved metrics CSV: %s" % FIT_CSV)
    print("Saved predictions CSV: %s" % PRED_CSV)
    print("Saved slopes CSV: %s" % SLOPE_CSV)
    print("Saved %d fit figures in: %s" % (len(fit_fig_paths), FIT_FIG_DIR))
    print("Saved BIC figure: %s" % BIC_FIG_PNG)
    print("Saved BIC figure: %s" % BIC_FIG_SVG)
    print("Saved adjusted R2 figure: %s" % ADJ_R2_FIG_PNG)
    print("Saved adjusted R2 figure: %s" % ADJ_R2_FIG_SVG)


if __name__ == "__main__":
    main()
