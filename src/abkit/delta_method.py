import numpy as np
from scipy import stats

from abkit.result import Result


def _ratio_and_var(num: np.ndarray, den: np.ndarray) -> tuple[float, float]:
    n = len(num)
    mu_n, mu_d = np.mean(num), np.mean(den)
    var_n, var_d = np.var(num, ddof=1), np.var(den, ddof=1)
    cov = np.cov(num, den)[0, 1]
    var = (var_n / mu_d**2 - 2 * mu_n * cov / mu_d**3 + mu_n**2 * var_d / mu_d**4) / n
    return mu_n / mu_d, var


def delta_method_ratio(
    num_t: np.ndarray,
    den_t: np.ndarray,
    num_c: np.ndarray,
    den_c: np.ndarray,
    alpha: float = 0.05,
) -> Result:
    """Difference in ratio metrics sum(num)/sum(den), with delta-method SE."""
    r_t, v_t = _ratio_and_var(num_t, den_t)
    r_c, v_c = _ratio_and_var(num_c, den_c)
    diff, se = r_t - r_c, np.sqrt(v_t + v_c)
    z = stats.norm.ppf(1 - alpha / 2)
    p_value = 2 * stats.norm.sf(abs(diff / se))
    return Result(float(diff), float(diff - z * se), float(diff + z * se), float(p_value))
