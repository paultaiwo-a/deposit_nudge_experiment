import math

from scipy import stats

from abkit.result import Result


def two_prop_ztest(x_t: int, n_t: int, x_c: int, n_c: int, alpha: float = 0.05) -> Result:
    """Two-sided z-test for p_t - p_c. Pooled SE for the test, unpooled SE for the CI."""
    p_t, p_c = x_t / n_t, x_c / n_c
    diff = p_t - p_c
    p_pool = (x_t + x_c) / (n_t + n_c)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n_t + 1 / n_c))
    se = math.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    p_value = 2 * stats.norm.sf(abs(diff / se_pool))
    z = stats.norm.ppf(1 - alpha / 2)
    return Result(diff, diff - z * se, diff + z * se, float(p_value))
