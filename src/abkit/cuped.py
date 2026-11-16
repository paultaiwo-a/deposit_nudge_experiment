import numpy as np


def cuped_adjust(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Remove the part of y explained by pre-period covariate x. Pass all arms pooled."""
    theta = np.cov(y, x)[0, 1] / np.var(x, ddof=1)
    return y - theta * (x - np.mean(x))
