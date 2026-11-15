"""Power analysis for the brief, using control-arm baselines only."""

import duckdb
import numpy as np
from statsmodels.stats.power import NormalIndPower, TTestIndPower
from statsmodels.stats.proportion import proportion_effectsize

ALPHA = 0.05 / 2  # two treatment arms; Holm is at least this powerful
POWER = 0.8
N_PER_ARM = 21_000
TARGET_LIFT_PP = 0.0025


def main() -> None:
    with duckdb.connect("warehouse.duckdb", read_only=True) as con:
        p0, mu0, sd0 = con.execute(
            """
            select avg(conversion), avg(spend), stddev_samp(spend)
            from raw_hillstrom where segment = 'No E-Mail'
            """
        ).fetchone()

    h = NormalIndPower().solve_power(alpha=ALPHA, power=POWER, nobs1=N_PER_ARM, ratio=1)
    mde_conv = np.sin(np.arcsin(np.sqrt(p0)) + h / 2) ** 2 - p0
    d = TTestIndPower().solve_power(alpha=ALPHA, power=POWER, nobs1=N_PER_ARM, ratio=1)
    n_target = NormalIndPower().solve_power(
        effect_size=proportion_effectsize(p0 + TARGET_LIFT_PP, p0), alpha=ALPHA, power=POWER
    )

    print(f"baseline conversion: {p0:.4%}")
    print(f"baseline deposit per user: {mu0:.3f} (sd {sd0:.2f})")
    print(f"MDE conversion at n={N_PER_ARM}: +{mde_conv:.4%} abs, {mde_conv / p0:+.0%} rel")
    print(f"MDE deposit per user at n={N_PER_ARM}: +{d * sd0:.3f}, {d * sd0 / mu0:+.0%} rel")
    print(f"n per arm for +{TARGET_LIFT_PP:.2%} conversion: {np.ceil(n_target):,.0f}")


if __name__ == "__main__":
    main()
