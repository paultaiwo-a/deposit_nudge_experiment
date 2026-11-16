import numpy as np
from sklearn.linear_model import LogisticRegression

from abkit import t_learner_uplift


def simulate(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    segment = rng.integers(0, 2, n)
    treated = rng.integers(0, 2, n)
    p = 0.1 + 0.2 * segment * treated
    return segment.reshape(-1, 1).astype(float), rng.random(n) < p, treated


def test_recovers_segment_uplift():
    # true uplift is 0.2 in segment 1 and 0 in segment 0
    rng = np.random.default_rng(0)
    X, y, treated = simulate(20000, rng)
    scores = t_learner_uplift(LogisticRegression(), X, y, treated, np.array([[0.0], [1.0]]))
    assert abs(scores[0]) < 0.02
    assert abs(scores[1] - 0.2) < 0.03


def test_no_effect_gives_near_zero_uplift():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(10000, 2))
    y = rng.random(10000) < 0.2
    treated = rng.integers(0, 2, 10000)
    scores = t_learner_uplift(LogisticRegression(), X, y, treated, X)
    assert abs(scores.mean()) < 0.02
