import math

from abkit import srm_check


def test_balanced_counts_give_p_of_one():
    assert srm_check([1000, 1000, 1000]) == 1.0


def test_known_chi_square():
    # chi2 = (0 + 400 + 400) / 100 = 8 with df=2, so p = exp(-4)
    assert math.isclose(srm_check([100, 80, 120]), math.exp(-4))


def test_unequal_ratios():
    assert srm_check([500, 1000], ratios=[1, 2]) == 1.0
