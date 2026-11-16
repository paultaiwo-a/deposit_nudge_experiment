import numpy as np
from sklearn.base import ClassifierMixin, clone


def t_learner_uplift(
    model: ClassifierMixin,
    X_train: np.ndarray,
    y_train: np.ndarray,
    treated_train: np.ndarray,
    X_score: np.ndarray,
) -> np.ndarray:
    """Fit one model per arm and return P(y | treated) - P(y | control) for X_score."""
    treated_train = np.asarray(treated_train, dtype=bool)
    m_t = clone(model).fit(X_train[treated_train], y_train[treated_train])
    m_c = clone(model).fit(X_train[~treated_train], y_train[~treated_train])
    return m_t.predict_proba(X_score)[:, 1] - m_c.predict_proba(X_score)[:, 1]
