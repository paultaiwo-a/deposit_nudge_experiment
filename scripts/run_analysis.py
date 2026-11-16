"""Run the pre-registered analysis and write results/results.json and charts."""

import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

from abkit import (
    Result,
    bootstrap_ci,
    cuped_adjust,
    delta_method_ratio,
    holm,
    srm_check,
    two_prop_ztest,
    welch_ttest,
)

DB_PATH = "warehouse.duckdb"
OUT = Path("results")
CONTROL = "control"
ARMS = ["mens_email", "womens_email"]
ARM_LABELS = {"mens_email": "Mens E-Mail", "womens_email": "Womens E-Mail"}
ARM_COLORS = {"mens_email": "#2a78d6", "womens_email": "#eb6834"}
METRIC_LABELS = {
    "funding_rate": "Funding rate",
    "visit_rate": "Visit rate",
    "deposit_per_user": "Deposit per user",
    "deposit_per_user_cuped": "Deposit per user (CUPED)",
    "deposit_per_funded_user": "Deposit per funded user",
}
ALPHA = 0.05
SRM_ALPHA = 0.001
GUARDRAIL_FLOOR = -0.20


def load() -> dict[str, dict[str, np.ndarray]]:
    with duckdb.connect(DB_PATH, read_only=True) as con:
        d = con.sql(
            "select arm, pre_deposits, visited, funded, deposit_amount from fct_experiment_metrics"
        ).fetchnumpy()
    arm = np.asarray(d.pop("arm"))
    d = {k: np.asarray(v, dtype=float) for k, v in d.items()}
    d["deposit_cuped"] = cuped_adjust(d["deposit_amount"], d["pre_deposits"])
    return {a: {k: v[arm == a] for k, v in d.items()} for a in [CONTROL, *ARMS]}


def summarize(r: Result, baseline: float) -> dict:
    return {
        **r._asdict(),
        "baseline": baseline,
        "rel_estimate": r.estimate / baseline,
        "rel_ci_low": r.ci_low / baseline,
        "rel_ci_high": r.ci_high / baseline,
    }


def compare(t: dict[str, np.ndarray], c: dict[str, np.ndarray]) -> dict:
    def prop(col: str) -> Result:
        return two_prop_ztest(int(t[col].sum()), len(t[col]), int(c[col].sum()), len(c[col]))

    deposit = summarize(
        welch_ttest(t["deposit_amount"], c["deposit_amount"]), c["deposit_amount"].mean()
    )
    deposit["bootstrap_ci_low"], deposit["bootstrap_ci_high"] = bootstrap_ci(
        t["deposit_amount"], c["deposit_amount"]
    )
    return {
        "funding_rate": summarize(prop("funded"), c["funded"].mean()),
        "visit_rate": summarize(prop("visited"), c["visited"].mean()),
        "deposit_per_user": deposit,
        "deposit_per_user_cuped": summarize(
            welch_ttest(t["deposit_cuped"], c["deposit_cuped"]), c["deposit_amount"].mean()
        ),
        "deposit_per_funded_user": summarize(
            delta_method_ratio(t["deposit_amount"], t["funded"], c["deposit_amount"], c["funded"]),
            c["deposit_amount"].sum() / c["funded"].sum(),
        ),
    }


def decide(results: dict, srm_ok: bool) -> str | None:
    passing = [
        arm
        for arm in ARMS
        if srm_ok
        and results[arm]["funding_rate"]["estimate"] > 0
        and results[arm]["funding_rate"]["p_holm"] < ALPHA
        and results[arm]["deposit_per_funded_user"]["rel_ci_high"] >= GUARDRAIL_FLOOR
    ]
    return max(passing, key=lambda a: results[a]["funding_rate"]["estimate"], default=None)


def funding_chart(results: dict) -> plt.Figure:
    labels = ["Control"] + [ARM_LABELS[a] for a in ARMS]
    base = results[ARMS[0]]["funding_rate"]["baseline"]
    rates = [base] + [base + results[a]["funding_rate"]["estimate"] for a in ARMS]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, rates, color=["#8a8984"] + [ARM_COLORS[a] for a in ARMS])
    ax.bar_label(bars, labels=[f"{r:.2%}" for r in rates])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=1))
    ax.set_title("Funding rate by arm")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def lift_chart(results: dict) -> plt.Figure:
    metrics = list(METRIC_LABELS)
    y = np.arange(len(metrics))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, arm in enumerate(ARMS):
        rows = [results[arm][m] for m in metrics]
        est = np.array([r["rel_estimate"] for r in rows])
        err = [est - [r["rel_ci_low"] for r in rows], [r["rel_ci_high"] for r in rows] - est]
        ax.errorbar(
            est,
            y + (i - 0.5) * 0.3,
            xerr=err,
            fmt="o",
            color=ARM_COLORS[arm],
            label=ARM_LABELS[arm],
        )
    ax.axvline(0, color="#52514e", linewidth=1)
    ax.set_yticks(y, [METRIC_LABELS[m] for m in metrics])
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_title("Relative lift vs control, 95% CI")
    ax.legend(loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def main() -> None:
    data = load()
    counts = {a: len(data[a]["funded"]) for a in data}
    srm_p = srm_check(list(counts.values()))
    results = {arm: compare(data[arm], data[CONTROL]) for arm in ARMS}

    p_holm = holm([results[a]["funding_rate"]["p_value"] for a in ARMS])
    for arm, p in zip(ARMS, p_holm, strict=True):
        results[arm]["funding_rate"]["p_holm"] = p
        results[arm]["incremental_funded_per_10k"] = results[arm]["funding_rate"]["estimate"] * 1e4
        results[arm]["incremental_deposits_per_10k"] = (
            results[arm]["deposit_per_user_cuped"]["estimate"] * 1e4
        )

    srm_ok = srm_p >= SRM_ALPHA
    output = {
        "counts": counts,
        "srm_p_value": srm_p,
        "srm_ok": srm_ok,
        "results": results,
        "ship": decide(results, srm_ok),
    }

    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(output, indent=2))
    funding_chart(results).savefig(OUT / "funding_rate.png", dpi=150)
    lift_chart(results).savefig(OUT / "lift_chart.png", dpi=150)
    print(json.dumps({k: output[k] for k in ("counts", "srm_p_value", "ship")}, indent=2))


if __name__ == "__main__":
    main()
