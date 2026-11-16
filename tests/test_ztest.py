import pytest

from abkit import two_prop_ztest


def test_hand_computed():
    # p_t=0.06, p_c=0.04, pooled 0.05, SE = sqrt(0.05*0.95*2/1000) = 0.009747, z = 2.0520
    r = two_prop_ztest(60, 1000, 40, 1000)
    assert r.estimate == pytest.approx(0.02)
    assert r.p_value == pytest.approx(0.04016, abs=1e-4)


def test_ci_uses_unpooled_se():
    # SE = sqrt(0.06*0.94/1000 + 0.04*0.96/1000) = 0.009737
    r = two_prop_ztest(60, 1000, 40, 1000)
    assert r.ci_high - r.estimate == pytest.approx(1.95996 * 0.009737, abs=1e-5)


def test_no_difference():
    r = two_prop_ztest(50, 1000, 50, 1000)
    assert r.estimate == 0
    assert r.p_value == pytest.approx(1.0)
