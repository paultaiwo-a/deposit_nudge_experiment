import numpy as np
from scipy import stats

from abkit.result import Result


def welch_ttest(t: np.ndarray, c: np.ndarray, alpha: float = 0.05) -> Result:
    """Welch t-test for mean(t) - mean(c)."""
    res = stats.ttest_ind(t, c, equal_var=False)
    ci = res.confidence_interval(1 - alpha)
    return Result(float(np.mean(t) - np.mean(c)), float(ci.low), float(ci.high), float(res.pvalue))
