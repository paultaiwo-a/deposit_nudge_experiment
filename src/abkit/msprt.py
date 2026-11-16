import numpy as np


def msprt_log_lambda(diff: np.ndarray, var: np.ndarray, tau2: float) -> np.ndarray:
    """Log mixture likelihood ratio for a difference in means with a N(0, tau2) prior.

    diff is the observed difference, var its variance at each look.
    """
    return 0.5 * np.log(var / (var + tau2)) + diff**2 * tau2 / (2 * var * (var + tau2))


def always_valid_pvalues(diff: np.ndarray, var: np.ndarray, tau2: float) -> np.ndarray:
    """mSPRT p-values at each look. Safe to check after every look."""
    log_lambda = msprt_log_lambda(np.asarray(diff), np.asarray(var), tau2)
    return np.minimum.accumulate(np.exp(-np.maximum(log_lambda, 0)))
