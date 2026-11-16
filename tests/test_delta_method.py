import numpy as np
import pytest

from abkit import delta_method_ratio, welch_ttest


def test_constant_denominator_reduces_to_mean_difference():
    rng = np.random.default_rng(7)
    a, b = rng.normal(2, 1, 3000), rng.normal(1.8, 1, 3000)
    ones = np.ones(3000)
    r = delta_method_ratio(a, ones, b, ones)
    w = welch_ttest(a, b)
    assert r.estimate == pytest.approx(w.estimate)
    assert r.ci_high - r.ci_low == pytest.approx(w.ci_high - w.ci_low, rel=0.01)


def test_ci_coverage_by_simulation():
    rng = np.random.default_rng(8)
    covered = 0
    for _ in range(400):
        den_t, den_c = rng.poisson(3, 500) + 1, rng.poisson(3, 500) + 1
        num_t, num_c = rng.gamma(2, den_t), rng.gamma(2, den_c)
        r = delta_method_ratio(num_t, den_t, num_c, den_c)
        covered += r.ci_low <= 0 <= r.ci_high
    assert covered / 400 == pytest.approx(0.95, abs=0.03)
