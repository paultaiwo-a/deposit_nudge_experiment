from collections.abc import Sequence

from scipy import stats


def srm_check(counts: Sequence[int], ratios: Sequence[float] | None = None) -> float:
    """Chi-square p-value for observed arm sizes vs the expected allocation ratios."""
    total = sum(counts)
    ratios = ratios or [1.0] * len(counts)
    expected = [total * r / sum(ratios) for r in ratios]
    return float(stats.chisquare(counts, expected).pvalue)
