import numpy as np
import pytest

from abkit import cuped_adjust


def test_removes_covariate_variance():
    rng = np.random.default_rng(4)
    x = rng.normal(10, 3, 20000)
    y = 2 * x + rng.normal(0, 1, 20000)
    y_adj = cuped_adjust(y, x)
    assert np.var(y) == pytest.approx(37, rel=0.05)
    assert np.var(y_adj) == pytest.approx(1, rel=0.05)


def test_preserves_mean():
    rng = np.random.default_rng(5)
    x = rng.normal(5, 1, 1000)
    y = x + rng.normal(0, 1, 1000)
    assert np.mean(cuped_adjust(y, x)) == pytest.approx(np.mean(y))


def test_preserves_treatment_effect():
    rng = np.random.default_rng(6)
    n = 20000
    x = rng.normal(0, 2, n)
    treated = rng.integers(0, 2, n).astype(bool)
    y = x + 0.3 * treated + rng.normal(0, 0.5, n)
    y_adj = cuped_adjust(y, x)
    assert y_adj[treated].mean() - y_adj[~treated].mean() == pytest.approx(0.3, abs=0.02)
