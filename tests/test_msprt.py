import math

import numpy as np
import pytest

from abkit import always_valid_pvalues, msprt_log_lambda


def test_zero_difference():
    # sqrt(V / (V + tau2)) = sqrt(1 / 4) = 0.5
    assert math.exp(msprt_log_lambda(0.0, 1.0, 3.0)) == pytest.approx(0.5)


def test_hand_computed():
    # sqrt(1/2) * exp(4 * 1 / (2 * 1 * 2)) = 0.7071 * e
    assert math.exp(msprt_log_lambda(2.0, 1.0, 1.0)) == pytest.approx(math.sqrt(0.5) * math.e)


def test_pvalues_never_increase():
    rng = np.random.default_rng(0)
    diff = rng.normal(0, 0.1, 200)
    p = always_valid_pvalues(diff, np.full(200, 0.01), 0.01)
    assert np.all(np.diff(p) <= 0)
    assert p.max() <= 1


def test_false_positive_rate_under_continuous_peeking():
    rng = np.random.default_rng(1)
    n = np.arange(1, 1001)
    sims, rejected = 400, 0
    for _ in range(sims):
        diff = np.cumsum(rng.normal(0, 1, 1000) - rng.normal(0, 1, 1000)) / n
        rejected += always_valid_pvalues(diff, 2 / n, 0.1)[-1] < 0.05
    assert rejected / sims < 0.05 + 0.03


def test_detects_real_effect():
    rng = np.random.default_rng(2)
    n = np.arange(1, 2001)
    diff = np.cumsum(rng.normal(0.3, 1, 2000) - rng.normal(0, 1, 2000)) / n
    assert always_valid_pvalues(diff, 2 / n, 0.1)[-1] < 0.001
