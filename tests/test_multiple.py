import pytest
from statsmodels.stats.multitest import multipletests

from abkit import holm


def test_hand_computed():
    # sorted: 0.01*3 = 0.03, 0.03*2 = 0.06, 0.04*1 = 0.04 -> running max 0.06
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])


def test_matches_statsmodels():
    p = [0.002, 0.2, 0.013, 0.04, 0.9]
    assert holm(p) == pytest.approx(multipletests(p, method="holm")[1].tolist())


def test_capped_at_one():
    assert max(holm([0.6, 0.7])) == 1.0
