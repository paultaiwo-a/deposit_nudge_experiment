import numpy as np
import pytest

from abkit import welch_ttest


def test_hand_computed():
    # means 2.5 and 6, SE = sqrt(1.6667/4 + 10/5) = 1.5546, t = -2.2514, df = 5.52
    r = welch_ttest(np.array([1, 2, 3, 4]), np.array([2, 4, 6, 8, 10]))
    assert r.estimate == pytest.approx(-3.5)
    assert r.p_value == pytest.approx(0.0693, abs=1e-3)
    assert r.ci_low < -3.5 < r.ci_high


def test_detects_large_effect():
    rng = np.random.default_rng(1)
    r = welch_ttest(rng.normal(1, 1, 5000), rng.normal(0, 3, 5000))
    assert r.estimate == pytest.approx(1, abs=0.15)
    assert r.p_value < 1e-6
