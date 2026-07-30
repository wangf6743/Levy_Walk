from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import math
from typing import Iterable, Optional, Union

import numpy as np


class Dist(IntEnum):
    EXPONENTIAL = 1
    TRUNCATED_PARETO = 2


DIST_ALIASES = {
    "exponential": Dist.EXPONENTIAL,
    "exp": Dist.EXPONENTIAL,
    "truncated_pareto": Dist.TRUNCATED_PARETO,
    "truncated-pareto": Dist.TRUNCATED_PARETO,
    "tp": Dist.TRUNCATED_PARETO,
}

DIST_NAMES = {
    Dist.EXPONENTIAL: "Exponential",
    Dist.TRUNCATED_PARETO: "Truncated Pareto",
}


@dataclass
class FitResult:
    dist: Dist
    n_original: int
    n_fitted: int
    xmin: float
    xmax: float
    alpha: Optional[float] = None
    ks_d: Optional[float] = None
    log_likelihood: Optional[float] = None
    p_value: Optional[float] = None
    aic_weight: Optional[float] = None
    alt: Optional["FitResult"] = None

    @property
    def name(self) -> str:
        return DIST_NAMES[self.dist]

    def parameters(self) -> dict[str, float]:
        return {
            "alpha_or_lambda": self.alpha,
            "xmin": self.xmin,
            "xmax": self.xmax,
        }


def _as_dist(dist: Union[str, int, Dist]) -> Dist:
    if isinstance(dist, Dist):
        return dist
    if isinstance(dist, str):
        key = dist.strip().lower().replace(" ", "_")
        if key not in DIST_ALIASES:
            raise ValueError(f"Only exponential and truncated_pareto are supported: {dist!r}")
        return DIST_ALIASES[key]
    return Dist(int(dist))


def clean_steps(steps: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(steps), dtype=float)
    arr = arr[np.isfinite(arr)]
    arr = arr[arr > 0]
    arr.sort()
    if arr.size == 0:
        raise ValueError("No positive finite step lengths were supplied.")
    return arr


def trim_steps(steps: np.ndarray, xmin: float = 0.0, xmax: float = math.inf) -> np.ndarray:
    steps = np.asarray(steps, dtype=float)
    return np.sort(steps[(steps >= xmin) & (steps <= xmax)])


def source_style_steps_from_xy(
    x: Iterable[float],
    y: Optional[Iterable[float]] = None,
    z: Optional[Iterable[float]] = None,
    *,
    dimension: Union[str, int] = "x",
    times: Optional[Iterable[object]] = None,
    max_gap_seconds: float = 0.0,
    coalesce: bool = True,
    xmin: float = 0.0,
    xmax: float = math.inf,
) -> np.ndarray:
    dim = dimension.lower() if isinstance(dimension, str) else int(dimension)
    if dim in ("x", "long", "longitude", 0):
        values = np.asarray(list(x), dtype=float)
    elif dim in ("y", "lat", "latitude", 1):
        if y is None:
            raise ValueError("dimension='y' requires y values.")
        values = np.asarray(list(y), dtype=float)
    elif dim in ("z", "depth", 2):
        if z is None:
            raise ValueError("dimension='z' requires z values.")
        values = np.asarray(list(z), dtype=float)
    else:
        raise ValueError("dimension must be 'x'/0, 'y'/1, or 'z'/2.")

    values = values[np.isfinite(values)]
    if values.size < 2:
        return np.array([], dtype=float)

    signed_steps = values[:-1] - values[1:]
    if times is None:
        gaps = np.zeros_like(signed_steps, dtype=float)
    else:
        t = np.asarray(list(times))
        if t.size != values.size:
            raise ValueError("times must have the same length as the selected coordinate series.")
        if np.issubdtype(t.dtype, np.datetime64):
            gaps = np.diff(t).astype("timedelta64[ns]").astype(float) / 1e9
        else:
            gaps = np.diff(t.astype(float))

    xmin_eff = 1e-10 if xmin is None or xmin <= 0 else float(xmin)
    xmax_eff = math.inf if xmax is None or xmax <= 0 else float(xmax)

    def keep_step(step_value: float) -> None:
        if xmin_eff <= step_value <= xmax_eff:
            filtered_steps.append(step_value)

    filtered_steps: list[float] = []

    if not coalesce:
        for signed_step, gap in zip(signed_steps, gaps):
            if max_gap_seconds > 0 and gap > max_gap_seconds:
                continue
            abs_step = abs(float(signed_step))
            keep_step(abs_step)
        return np.asarray(filtered_steps, dtype=float)

    step = 0.0
    last_step = 0.0

    for signed_step, gap in zip(signed_steps, gaps):
        signed_step = float(signed_step)
        abs_step = abs(signed_step)

        if max_gap_seconds > 0 and gap > max_gap_seconds:
            keep_step(step)
            step = 0.0
            last_step = 0.0
            continue

        if np.sign(signed_step) == np.sign(last_step):
            step += abs_step
        else:
            keep_step(step)
            step = abs_step

        last_step = signed_step

    keep_step(step)

    return np.asarray(filtered_steps, dtype=float)


def exponential_mle(steps: np.ndarray, xmin: float) -> float:
    shifted_sum = float(np.sum(steps - xmin))
    return len(steps) / shifted_sum if shifted_sum > 0 else 0.0


def power_mle(steps: np.ndarray, xmin: float) -> float:
    total = float(np.sum(np.log(steps / xmin)))
    return 1.0 + len(steps) / total if total > 0 else 0.0


def truncated_pareto_mle(steps: np.ndarray, xmin: float, xmax: float) -> float:
    """Match MBA_MLE_Analysis MLEX.TrucatedPareto_MLE.

    The C# code solves White et al.'s truncated-Pareto score equation by a
    simple directional search over lambda, then returns mu = -lambda.
    """
    mean_log_x = float(np.mean(np.log(steps)))
    log_xmax = math.log(xmax)
    log_xmin = math.log(xmin)

    lambda_value = -power_mle(steps, xmin)
    best_lambda = lambda_value
    last_y = math.inf
    best_y = math.inf
    q = 3.3
    lambda_inc = lambda_value / q
    lambda_value -= lambda_inc
    stop = 0.001
    max_count = 100
    count = 0
    y = 1.0

    while y != 0.0 and abs(lambda_inc) > stop and count < max_count:
        count += 1
        lambda_value += lambda_inc
        lambda_plus_1 = lambda_value + 1.0

        try:
            xmax_power = xmax ** lambda_plus_1
            xmin_power = xmin ** lambda_plus_1
            y = (
                -mean_log_x
                - 1.0 / lambda_plus_1
                + (xmax_power * log_xmax - xmin_power * log_xmin)
                / (xmax_power - xmin_power)
            )
            y = abs(y)
        except (OverflowError, ZeroDivisionError, ValueError):
            y = math.inf

        if y < best_y:
            best_lambda = lambda_value
            best_y = y

        if y > abs(last_y):
            lambda_inc = -(lambda_inc / q)

        last_y = y

    return -best_lambda



def exponential_llh(steps: np.ndarray, lam: float, xmin: float) -> float:
    if lam <= 0:
        return -math.inf
    return float(len(steps) * (math.log(lam) + lam * xmin) - lam * np.sum(steps))


def truncated_pareto_llh(steps: np.ndarray, mu: float, xmin: float, xmax: float) -> float:
    if xmin <= 0 or xmax <= xmin:
        return -math.inf

    term1 = xmin ** (1.0 - mu) - xmax ** (1.0 - mu)
    if term1 == 0.0:
        return -math.inf

    norm = (mu - 1.0) / term1
    if norm <= 0 or not math.isfinite(norm):
        return -math.inf

    return float(len(steps) * math.log(norm) - mu * np.sum(np.log(steps)))


def deterministic_sample(dist: Dist, n: int, *, alpha: float, xmin: float, xmax: float) -> np.ndarray:
    u = np.arange(n, dtype=float) / float(n)
    u = np.clip(u, 0.0, 1.0 - 1e-12)

    if dist == Dist.EXPONENTIAL:
        values = xmin - np.log(1.0 - u) / alpha
    elif dist == Dist.TRUNCATED_PARETO:
        if abs(alpha - 1.0) < 1e-10:
            values = xmin * (xmax / xmin) ** u
        else:
            beta = alpha - 1.0
            term1 = 1.0 - (xmax / xmin) ** (-beta)
            term2 = (xmax / xmin) ** (-beta)
            term3 = -1.0 / beta
            values = xmin * ((1.0 - u) * term1 + term2) ** term3
    else:
        raise ValueError(dist)

    return np.sort(np.asarray(values, dtype=float))


def random_sample(
    dist: Dist,
    n: int,
    *,
    rng: np.random.Generator,
    alpha: float,
    xmin: float,
    xmax: float,
) -> np.ndarray:
    u = rng.random(n)
    if dist == Dist.EXPONENTIAL:
        values = xmin - np.log(1.0 - u) / alpha
    elif dist == Dist.TRUNCATED_PARETO:
        if abs(alpha - 1.0) < 1e-10:
            values = xmin * (xmax / xmin) ** u
        else:
            power = 1.0 - alpha
            values = (xmin ** power + u * (xmax ** power - xmin ** power)) ** (1.0 / power)
    else:
        raise ValueError(dist)
    return np.sort(values)


def ks_distance(s1: np.ndarray, s2: np.ndarray) -> float:
    a = np.sort(np.asarray(s1, dtype=float))
    b = np.sort(np.asarray(s2, dtype=float))
    values = np.unique(np.concatenate([a, b]))
    cdf_a = np.searchsorted(a, values, side="right") / len(a)
    cdf_b = np.searchsorted(b, values, side="right") / len(b)
    return float(np.max(np.abs(cdf_a - cdf_b)))


def aicc_weights(llh1: float, llh2: float, n: int, dist1: Dist, dist2: Dist) -> tuple[float, float]:
    def k_for(dist: Dist) -> int:
        return 3 if dist == Dist.TRUNCATED_PARETO else 2

    def aicc(llh: float, k: int) -> float:
        if n <= k + 1:
            return math.inf
        return -2.0 * llh + 2.0 * k + (2.0 * k * (k + 1.0)) / (n - k - 1.0)

    a1 = aicc(llh1, k_for(dist1))
    a2 = aicc(llh2, k_for(dist2))
    amin = min(a1, a2)
    w1 = math.exp(-0.5 * (a1 - amin))
    w2 = math.exp(-0.5 * (a2 - amin))
    total = w1 + w2
    return w1 / total, w2 / total


def _estimate_params(dist: Dist, steps: np.ndarray, xmin: float, xmax: float) -> dict[str, float]:
    if dist == Dist.EXPONENTIAL:
        return {"alpha": exponential_mle(steps, xmin)}
    if dist == Dist.TRUNCATED_PARETO:
        return {"alpha": truncated_pareto_mle(steps, xmin, xmax)}
    raise ValueError(dist)


def _llh(dist: Dist, steps: np.ndarray, xmin: float, xmax: float, params: dict[str, float]) -> float:
    if dist == Dist.EXPONENTIAL:
        return exponential_llh(steps, params["alpha"], xmin)
    if dist == Dist.TRUNCATED_PARETO:
        return truncated_pareto_llh(steps, params["alpha"], xmin, xmax)
    raise ValueError(dist)


def search_xmin(
    steps: np.ndarray,
    dist: Dist,
    xmax: float,
    *,
    fitting: str = "limited",
    worse_count_limit: int = 5,
) -> tuple[float, float, dict[str, float]]:
    best_d = math.inf
    best_xmin = float(steps[0])
    best_params: dict[str, float] = {}
    worse_count = 0

    for xmin in np.unique(steps):
        test_steps = trim_steps(steps, float(xmin), xmax)
        if len(test_steps) < 2:
            continue
        params = _estimate_params(dist, test_steps, float(xmin), xmax)
        model_steps = deterministic_sample(dist, len(test_steps), xmin=float(xmin), xmax=xmax, **params)
        d = ks_distance(test_steps, model_steps)

        if fitting == "best" and len(test_steps) > 1:
            d *= math.log(len(steps)) / math.log(len(test_steps))

        if d < best_d:
            best_d = d
            best_xmin = float(xmin)
            best_params = params
            worse_count = 0
        else:
            worse_count += 1

        if fitting != "best" and worse_count > worse_count_limit:
            break

    return best_xmin, best_d, best_params


def search_xmax(
    steps: np.ndarray,
    dist: Dist,
    xmin: float,
    *,
    fitting: str = "limited",
    worse_count_limit: int = 5,
) -> tuple[float, float, dict[str, float]]:
    best_d = math.inf
    best_xmax = float(steps[-1])
    best_params: dict[str, float] = {}
    worse_count = 0

    for xmax in np.unique(steps)[::-1]:
        xmax = float(xmax)
        if xmax <= xmin:
            continue
        test_steps = trim_steps(steps, xmin, xmax)
        if len(test_steps) < 2:
            continue
        params = _estimate_params(dist, test_steps, xmin, xmax)
        model_steps = deterministic_sample(dist, len(test_steps), xmin=xmin, xmax=xmax, **params)
        d = ks_distance(test_steps, model_steps)

        if fitting == "best" and len(test_steps) > 1:
            d *= math.log(len(steps)) / math.log(len(test_steps))

        if d < best_d:
            best_d = d
            best_xmax = xmax
            best_params = params
            worse_count = 0
        else:
            worse_count += 1

        if fitting != "best" and worse_count > worse_count_limit:
            break

    return best_xmax, best_d, best_params


def _make_result(
    dist: Dist,
    n_original: int,
    fitted: np.ndarray,
    xmin: float,
    xmax: float,
    params: dict[str, float],
    d: float,
) -> FitResult:
    return FitResult(
        dist=dist,
        n_original=n_original,
        n_fitted=len(fitted),
        xmin=float(xmin),
        xmax=float(xmax),
        alpha=params.get("alpha"),
        ks_d=float(d),
        log_likelihood=float(_llh(dist, fitted, xmin, xmax, params)),
    )


def fit_distribution(
    steps: Iterable[float],
    dist: Union[str, int, Dist] = "exponential",
    *,
    alt_dist: Optional[Union[str, int, Dist]] = "truncated_pareto",
    fitting: str = "limited",
    xmin: Optional[float] = None,
    xmax: Optional[float] = None,
    worse_count_limit: int = 5,
    p_test: bool = False,
    n_tests: int = 1000,
    random_seed: Optional[int] = None,
) -> FitResult:
    dist = _as_dist(dist)
    alt = _as_dist(alt_dist) if alt_dist is not None else None
    steps_arr = clean_steps(steps)
    n_original = len(steps_arr)
    xmin0 = float(steps_arr[0] if xmin is None else xmin)
    xmax0 = float(steps_arr[-1] if xmax is None else xmax)

    if fitting not in {"none", "limited", "best"}:
        raise ValueError("fitting must be 'none', 'limited', or 'best'")

    if fitting == "none":
        fitted = trim_steps(steps_arr, xmin0, xmax0)
        params = _estimate_params(dist, fitted, xmin0, xmax0)
        model_steps = deterministic_sample(dist, len(fitted), xmin=xmin0, xmax=xmax0, **params)
        d = ks_distance(fitted, model_steps)
        result = _make_result(dist, n_original, fitted, xmin0, xmax0, params, d)
    elif dist == Dist.EXPONENTIAL:
        xmin_fit, d, params = search_xmin(
            steps_arr,
            dist,
            xmax0,
            fitting=fitting,
            worse_count_limit=worse_count_limit,
        )
        fitted = trim_steps(steps_arr, xmin_fit, xmax0)
        result = _make_result(dist, n_original, fitted, xmin_fit, xmax0, params, d)
    else:
        xmin_fit, _, _ = search_xmin(
            steps_arr,
            dist,
            xmax0,
            fitting=fitting,
            worse_count_limit=worse_count_limit,
        )
        trimmed = trim_steps(steps_arr, xmin_fit, xmax0)
        xmax_fit, d, params = search_xmax(
            trimmed,
            dist,
            xmin_fit,
            fitting=fitting,
            worse_count_limit=worse_count_limit,
        )
        fitted = trim_steps(steps_arr, xmin_fit, xmax_fit)
        result = _make_result(dist, n_original, fitted, xmin_fit, xmax_fit, params, d)

    if p_test:
        result.p_value = monte_carlo_p_value(
            result,
            n_tests=n_tests,
            random_seed=random_seed,
            fitting=fitting,
            worse_count_limit=worse_count_limit,
        )

    if alt is not None:
        alt_params = _estimate_params(alt, fitted, result.xmin, result.xmax)
        alt_model_steps = deterministic_sample(alt, len(fitted), xmin=result.xmin, xmax=result.xmax, **alt_params)
        alt_d = ks_distance(fitted, alt_model_steps)
        alt_result = _make_result(alt, n_original, fitted, result.xmin, result.xmax, alt_params, alt_d)
        if (
            len(fitted) > 4
            and math.isfinite(result.log_likelihood)
            and math.isfinite(alt_result.log_likelihood)
        ):
            result.aic_weight, alt_result.aic_weight = aicc_weights(
                result.log_likelihood,
                alt_result.log_likelihood,
                len(fitted),
                dist,
                alt,
            )
        result.alt = alt_result

    return result


def monte_carlo_p_value(
    result: FitResult,
    *,
    n_tests: int = 1000,
    random_seed: Optional[int] = None,
    fitting: str = "limited",
    worse_count_limit: int = 5,
) -> float:
    rng = np.random.default_rng(random_seed)
    greater = 0

    for _ in range(n_tests):
        synth = random_sample(
            result.dist,
            result.n_fitted,
            rng=rng,
            alpha=result.alpha,
            xmin=result.xmin,
            xmax=result.xmax,
        )
        try:
            synth_result = fit_distribution(
                synth,
                dist=result.dist,
                alt_dist=None,
                fitting=fitting,
                xmax=result.xmax,
                worse_count_limit=worse_count_limit,
                p_test=False,
            )
        except Exception:
            continue
        if synth_result.ks_d is not None and synth_result.ks_d > result.ks_d:
            greater += 1

    return greater / float(n_tests) if n_tests > 0 else math.nan
