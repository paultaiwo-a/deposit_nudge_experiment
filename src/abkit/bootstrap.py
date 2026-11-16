import numpy as np
from scipy import stats


def bootstrap_ci(
    t: np.ndarray, c: np.ndarray, alpha: float = 0.05, n_resamples: int = 2000, seed: int = 0
) -> tuple[float, float]:
    """Percentile bootstrap CI for mean(t) - mean(c)."""
    res = stats.bootstrap(
        (t, c),
        lambda a, b, axis: np.mean(a, axis=axis) - np.mean(b, axis=axis),
        confidence_level=1 - alpha,
        n_resamples=n_resamples,
        method="percentile",
        rng=np.random.default_rng(seed),
    )
    return float(res.confidence_interval.low), float(res.confidence_interval.high)
