import numpy as np
import pytest

from abkit import bootstrap_ci, welch_ttest


def test_matches_normal_ci_on_large_sample():
    rng = np.random.default_rng(2)
    t, c = rng.normal(0.5, 2, 4000), rng.normal(0, 2, 4000)
    low, high = bootstrap_ci(t, c)
    r = welch_ttest(t, c)
    assert low == pytest.approx(r.ci_low, abs=0.03)
    assert high == pytest.approx(r.ci_high, abs=0.03)


def test_reproducible_with_seed():
    rng = np.random.default_rng(3)
    t, c = rng.exponential(1, 500), rng.exponential(1, 500)
    assert bootstrap_ci(t, c, seed=7) == bootstrap_ci(t, c, seed=7)
