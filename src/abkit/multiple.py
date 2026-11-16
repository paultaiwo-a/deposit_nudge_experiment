import numpy as np


def holm(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, in the original order."""
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adjusted = np.maximum.accumulate((m - np.arange(m)) * p[order]).clip(max=1)
    out = np.empty(m)
    out[order] = adjusted
    return out.tolist()
