# this code is for the comparison between the composite Browian model
# and the Truncated Power Law model. It is based on the study "Vincent A. A. Jansen et al. ,Comment on “Lévy Walks Evolve Through Interaction Between Movement and Environmental Complexity”.Science335,918-918(2012).DOI:10.1126/science.1215747"
# The original R code is available at  https://www.researchgate.net/publication/281372271_CB_fit_AM

import argparse
import csv
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RSCRIPT = "Rscript"


R_FIT_SCRIPT = r"""
args <- commandArgs(trailingOnly=TRUE)
input_file <- args[[1]]
output_file <- args[[2]]
start_profile <- args[[3]]
column_index <- as.integer(args[[4]])

raw_data <- read.csv(input_file, header=FALSE, stringsAsFactors=FALSE)
data <- suppressWarnings(as.numeric(raw_data[[column_index]]))
data <- data[is.finite(data) & data > 0]
if (length(data) < 2) {
  stop("Need at least two positive finite step lengths")
}

if (start_profile == "mussel") {
  start.cb <- list(
    cb2=c(p=0.05, lb=c(0.1,1)),
    cb3=c(p=c(0.05,0.1), lb=c(0.1,1,3)),
    cb4=c(p=c(0.01,0.05,0.1), lb=c(0.6,0.1,1,3))
  )
} else {
  start.cb <- list(
    cb2=c(p=0.1, lb=c(0.1,0.01)),
    cb3=c(p=c(0.1,0.1), lb=c(0.1,0.01,0.001)),
    cb4=c(p=c(0.1,0.1,0.1), lb=c(0.1,0.1,0.01,0.001))
  )
}

am.fit <- function(data,start)
 {
   Exp.ml <- function(lb,set) length(set)*(log(lb)+lb*min(set))-lb*sum(set)
   PL.ml <- function(mu,set) length(set)*(log(mu-1)- log(min(set)^(1-mu)))-mu*sum(log(set))
   TPL.ml <- function(mu,set) length(set)*(log(mu-1)- log( (min(set))^(1-mu) - (max(set))^(1-mu) ))-
                   mu*sum(log(set))
   CB.pdf <- function(x,p,lb,k,lower)
   { pv <- numeric(k-1); for (i in 1:(k-1)) pv[i] <- exp(p[i])/(1+sum(exp(p)))
     lbv <- exp(lb)
     res <- (1-sum(pv))*lbv[k]*exp(lbv[k]*lower)*exp(-lbv[k]*x)
     for (j in 1:(k-1)) res <- (res+pv[j]*lbv[j]*exp(lbv[j]*lower)*exp(-lbv[j]*x))
     return(res)
   }
   CB2.ml <- function(x,set) sum(log(CB.pdf(set,x[1],c(x[2],x[3]),2,min(set))))
   CB3.ml <- function(x,set) sum(log(CB.pdf(set,c(x[1],x[2]),c(x[3],x[4],x[5]),3,min(set))))
   CB4.ml <- function(x,set) sum(log(CB.pdf(set,c(x[1],x[2],x[3]),c(x[4],x[5],x[6],x[7]),4,min(set))))
   p.tr <- function(k) sapply(1:k,function(x) log(temp[x]/(1-sum(temp[1:k]))))
   temp <- start$cb2; s.cb2 <- c(p.tr(1),log(temp[2:3]))
   temp <- start$cb3; s.cb3 <- c(p.tr(2),log(temp[3:5]))
   temp <- start$cb4; s.cb4 <- c(p.tr(3),log(temp[4:7]))
   back.tr <- function(x) exp(x)/(1+sum(exp(x)))
   exp.best <- function(set) 1/(sum(set)/length(set)-min(set))
   pl.best <- function(set) 1-length(set)/(length(set)*log(min(set))-sum(log(set)))
   lb <- exp.best(data); par <- list(lb); ml <- Exp.ml(lb,data)
   mu <- pl.best(data); par <- c(par,mu); ml <- c(ml,PL.ml(mu,data))
   TPL.f <- function(mu) TPL.ml(mu,set=data)
   tpl <- optimize(TPL.f,lower=1.1,upper=3,maximum=TRUE)
   par <- c(par,tpl$maximum); ml <- c(ml,tpl$objective)
   CB2.f <- function(x) CB2.ml(x,set=data)
   cb2 <- optim(s.cb2,CB2.f,control=list(fnscale=-1))
   p <- back.tr(cb2$par[1])
   par <- c(par,list(c(p,exp(cb2$par[2:3])))); ml <- c(ml,cb2$value)
   CB3.f <- function(x) CB3.ml(x,set=data)
   cb3 <- optim(s.cb3,CB3.f,control=list(fnscale=-1))
   p <- back.tr(cb3$par[1:2])
   par <- c(par,list(c(p,exp(cb3$par[3:5])))); ml <- c(ml,cb3$value)
   CB4.f <- function(x) CB4.ml(x,set=data)
   cb4 <- optim(s.cb4,CB4.f,control=list(fnscale=-1))
   p <- back.tr(cb4$par[1:3])
   par <- c(par,list(c(p,exp(cb4$par[4:7])))); ml <- c(ml,cb4$value)
   return(c(par,list(ml)))
 }

AIC.weights <- function(MLL,k=c(1,1,1,3,5,7))
 {
    AIC <- (-2*MLL+2*k)
    min.AIC <- min(AIC); diff <- AIC-min.AIC
    AIC.w <- numeric(length(MLL))
    for (i in 1:length(MLL)) AIC.w[i] <- exp(-diff[i]/2)/sum(exp(-diff/2))
    return(cbind(MLL,AIC,AIC.w))
  }

res <- am.fit(data,start.cb)
aic_table <- AIC.weights(res[[7]])
model_names <- c("exponential", "power_law", "truncated_power_law", "cb2", "cb3", "cb4")
n_components <- c(1, 1, 1, 2, 3, 4)
n_params <- c(1, 1, 1, 3, 5, 7)

empty_row <- function(model, i) {
  data.frame(
    model=model,
    n_components=n_components[i],
    n_params=n_params[i],
    n_steps=length(data),
    xmin=min(data),
    xmax=max(data),
    log_likelihood=aic_table[i, "MLL"],
    aic=aic_table[i, "AIC"],
    aic_weight=aic_table[i, "AIC.w"],
    lambda=NA_real_,
    mu=NA_real_,
    p1=NA_real_, p2=NA_real_, p3=NA_real_, p4=NA_real_,
    lb1=NA_real_, lb2=NA_real_, lb3=NA_real_, lb4=NA_real_
  )
}

rows <- list()
for (i in 1:6) rows[[i]] <- empty_row(model_names[i], i)
rows[[1]]$lambda <- res[[1]]
rows[[2]]$mu <- res[[2]]
rows[[3]]$mu <- res[[3]]

cb2 <- res[[4]]
rows[[4]]$p1 <- cb2[1]
rows[[4]]$p2 <- 1 - cb2[1]
rows[[4]]$lb1 <- cb2[2]
rows[[4]]$lb2 <- cb2[3]

cb3 <- res[[5]]
rows[[5]]$p1 <- cb3[1]
rows[[5]]$p2 <- cb3[2]
rows[[5]]$p3 <- 1 - cb3[1] - cb3[2]
rows[[5]]$lb1 <- cb3[3]
rows[[5]]$lb2 <- cb3[4]
rows[[5]]$lb3 <- cb3[5]

cb4 <- res[[6]]
rows[[6]]$p1 <- cb4[1]
rows[[6]]$p2 <- cb4[2]
rows[[6]]$p3 <- cb4[3]
rows[[6]]$p4 <- 1 - cb4[1] - cb4[2] - cb4[3]
rows[[6]]$lb1 <- cb4[4]
rows[[6]]$lb2 <- cb4[5]
rows[[6]]$lb3 <- cb4[6]
rows[[6]]$lb4 <- cb4[7]

out <- do.call(rbind, rows)
write.csv(out, output_file, row.names=FALSE)
"""


class RCompositeBrownianFit:
    """One model row returned by the R composite Brownian fitter."""

    def __init__(self, model, n_components, n_params, n_steps, xmin, xmax, log_likelihood, aic, aic_weight, lambda_=None, mu=None, p1=None, p2=None, p3=None, p4=None, lb1=None, lb2=None, lb3=None, lb4=None):
        self.model = model
        self.n_components = n_components
        self.n_params = n_params
        self.n_steps = n_steps
        self.xmin = xmin
        self.xmax = xmax
        self.log_likelihood = log_likelihood
        self.aic = aic
        self.aic_weight = aic_weight
        self.lambda_ = lambda_
        self.mu = mu
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.lb1 = lb1
        self.lb2 = lb2
        self.lb3 = lb3
        self.lb4 = lb4


def _optional_float(value):
    if value == "" or value.upper() == "NA":
        return None
    numeric = float(value)
    return numeric if math.isfinite(numeric) else None


def _read_fit_csv(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return [
            RCompositeBrownianFit(
                model=row["model"],
                n_components=int(row["n_components"]),
                n_params=int(row["n_params"]),
                n_steps=int(row["n_steps"]),
                xmin=float(row["xmin"]),
                xmax=float(row["xmax"]),
                log_likelihood=float(row["log_likelihood"]),
                aic=float(row["aic"]),
                aic_weight=float(row["aic_weight"]),
                lambda_=_optional_float(row["lambda"]),
                mu=_optional_float(row["mu"]),
                p1=_optional_float(row["p1"]),
                p2=_optional_float(row["p2"]),
                p3=_optional_float(row["p3"]),
                p4=_optional_float(row["p4"]),
                lb1=_optional_float(row["lb1"]),
                lb2=_optional_float(row["lb2"]),
                lb3=_optional_float(row["lb3"]),
                lb4=_optional_float(row["lb4"]),
            )
            for row in reader
        ]


def _write_steps_csv(steps, path):
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        for step in steps:
            try:
                value = float(step)
            except (TypeError, ValueError):
                continue
            if math.isfinite(value) and value > 0:
                writer.writerow([value])


def fit_composite_brownian_r(
    steps,
    output_csv=None,
    rscript=DEFAULT_RSCRIPT,
    start_profile="gps",
    column=1,
    keep_temp=False,
    timeout=None,
):
    """Run the original R composite Brownian fitter and return model rows.

    Parameters
    ----------
    steps:
        Either a sequence of step lengths or a CSV file path. For CSV input,
        `column` is 1-based and the file is read without a header, matching the
        original R example.
    output_csv:
        Optional path for the R result table. If omitted, a temporary file is
        used and parsed back into Python.
    start_profile:
        "gps" uses the later GPS starting values from `CB_fit_AM.txt`;
        "mussel" uses the earlier mussel starting values.
    """

    if start_profile not in {"gps", "mussel"}:
        raise ValueError("start_profile must be 'gps' or 'mussel'")
    if column < 1:
        raise ValueError("column must be 1-based")

    with tempfile.TemporaryDirectory(prefix="cb_r_fit_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        r_script = tmp_dir / "fit_cb.R"
        r_script.write_text(R_FIT_SCRIPT, encoding="utf-8")

        if isinstance(steps, (str, Path)):
            input_csv = Path(steps)
        else:
            input_csv = tmp_dir / "steps.csv"
            _write_steps_csv(steps, input_csv)

        result_csv = Path(output_csv) if output_csv is not None else tmp_dir / "cb_fit_results.csv"
        result_csv.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            rscript,
            str(r_script),
            str(input_csv),
            str(result_csv),
            start_profile,
            str(column),
        ]
        completed = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=timeout,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "R composite Brownian fit failed\n"
                f"command: {' '.join(cmd)}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )

        fits = _read_fit_csv(result_csv)
        if keep_temp and output_csv is None:
            kept_path = SCRIPT_DIR / "cb_fit_results.csv"
            kept_path.write_text(result_csv.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"Saved temporary R result table to: {kept_path}")
        return fits


def _format_optional(value):
    return "NA" if value is None else f"{value:.6g}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python interface for CB_fit_AM.txt R fitter")
    parser.add_argument("input_csv", type=Path, help="CSV containing step lengths")
    parser.add_argument("--output-csv", type=Path, default=None, help="where to save the R result table")
    parser.add_argument("--column", type=int, default=1, help="1-based CSV column containing step lengths")
    parser.add_argument("--rscript", default=DEFAULT_RSCRIPT, help="Rscript executable")
    parser.add_argument(
        "--start-profile",
        choices=["gps", "mussel"],
        default="gps",
        help="starting values profile from CB_fit_AM.txt",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    fits = fit_composite_brownian_r(
        args.input_csv,
        output_csv=args.output_csv,
        rscript=args.rscript,
        start_profile=args.start_profile,
        column=args.column,
    )

    for fit in fits:
        print(
            f"{fit.model:20s} "
            f"LL={fit.log_likelihood:.6g} "
            f"AIC={fit.aic:.6g} "
            f"AICw={fit.aic_weight:.6g} "
            f"lambda={_format_optional(fit.lambda_)} "
            f"mu={_format_optional(fit.mu)}"
        )


if __name__ == "__main__":
    main()
