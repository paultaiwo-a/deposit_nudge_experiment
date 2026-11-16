from typing import NamedTuple


class Result(NamedTuple):
    """Treatment minus control estimate with a confidence interval."""

    estimate: float
    ci_low: float
    ci_high: float
    p_value: float
