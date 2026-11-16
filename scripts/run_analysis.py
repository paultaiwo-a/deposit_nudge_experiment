"""Run the pre-registered analysis and write results/results.json and charts."""

import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np

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
    labels = ["No E-Mail", "Mens E-Mail", "Womens E-Mail"]
    base = results[ARMS[0]]["funding_rate"]["baseline"]
    rates = [base] + [base + results[a]["funding_rate"]["estimate"] for a in ARMS]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.bar(labels, [r * 100 for r in rates])
    ax.set_xlabel("Group")
    ax.set_ylabel("Funding rate (%)")
    ax.set_title("Funding Rate by Group")
    ax.grid(True, axis="y")
    fig.tight_layout()
    return fig


def lift_chart(results: dict) -> plt.Figure:
    metrics = list(METRIC_LABELS)
    x = np.arange(len(metrics))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 7))
    for i, arm in enumerate(ARMS):
        rows = [results[arm][m] for m in metrics]
        est = np.array([r["rel_estimate"] * 100 for r in rows])
        low = np.array([r["rel_ci_low"] * 100 for r in rows])
        high = np.array([r["rel_ci_high"] * 100 for r in rows])
        ax.bar(
            x + (i - 0.5) * width,
            est,
            width,
            yerr=[est - low, high - est],
            capsize=4,
            label=ARM_LABELS[arm],
        )
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(x, [METRIC_LABELS[m] for m in metrics], rotation=20, ha="right")
    ax.set_ylabel("Lift compared with no email (%)")
    ax.set_title("Lift Compared with No Email")
    ax.legend()
    ax.grid(True, axis="y")
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
