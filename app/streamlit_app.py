import json
from pathlib import Path

import pandas as pd
import streamlit as st

RESULTS = Path(__file__).resolve().parent.parent / "results"
ARMS = {"mens_email": "Creative A (Mens)", "womens_email": "Creative B (Womens)"}
METRICS = {
    "funding_rate": "Funding rate",
    "visit_rate": "Visit rate",
    "deposit_per_user": "Deposit per user",
    "deposit_per_user_cuped": "Deposit per user (CUPED)",
    "deposit_per_funded_user": "Deposit per funded user",
}

results = json.loads((RESULTS / "results.json").read_text())
uplift = json.loads((RESULTS / "uplift.json").read_text())
peeking = json.loads((RESULTS / "peeking.json").read_text())

st.set_page_config(page_title="Deposit-match nudge readout", layout="wide")
st.title("Deposit-match nudge: experiment readout")

ship = results["ship"]
if ship:
    st.success(f"Decision: ship {ARMS[ship]}")
else:
    st.error("Decision: do not ship")

st.subheader("Sample")
c1, c2 = st.columns(2)
c1.dataframe(pd.Series(results["counts"], name="users").rename({"control": "Control", **ARMS}))
c2.metric("SRM p-value", f"{results['srm_p_value']:.2f}", "pass" if results["srm_ok"] else "fail")

st.subheader("Effects vs control, 95% CI")
rows = []
for arm, label in ARMS.items():
    for key, name in METRICS.items():
        r = results["results"][arm][key]
        rows.append(
            {
                "arm": label,
                "metric": name,
                "control": r["baseline"],
                "lift": r["estimate"],
                "ci low": r["ci_low"],
                "ci high": r["ci_high"],
                "relative lift": f"{r['rel_estimate']:+.1%}",
                "p-value": f"{r['p_value']:.2g}",
            }
        )
st.dataframe(pd.DataFrame(rows), hide_index=True)

c1, c2 = st.columns(2)
c1.image(str(RESULTS / "funding_rate.png"))
c2.image(str(RESULTS / "lift_chart.png"))

st.subheader("Impact per 10,000 users")
cols = st.columns(len(ARMS))
for col, (arm, label) in zip(cols, ARMS.items(), strict=True):
    r = results["results"][arm]
    col.metric(f"{label}: extra funded accounts", f"{r['incremental_funded_per_10k']:.0f}")
    col.metric(f"{label}: extra deposits", f"{r['incremental_deposits_per_10k']:,.0f}")

st.subheader("Targeting (exploratory)")
cols = st.columns(len(ARMS))
for col, (arm, label) in zip(cols, ARMS.items(), strict=True):
    u = uplift[arm]
    col.markdown(f"**{label}**")
    col.metric("Qini AUC", f"{u['qini_auc']:.3f}")
    col.metric(
        "Uplift in top 30% vs average",
        f"{u['uplift_at_30pct']:.2%}",
        f"{u['uplift_at_30pct'] - u['average_uplift']:+.2%}",
    )
    col.dataframe(pd.DataFrame(u["segments"]).head(5), hide_index=True)
st.image(str(RESULTS / "qini.png"), width=700)

st.subheader("Why not peek: A/A simulation")
c1, c2 = st.columns([1, 2])
c1.metric("Naive z-test, 100 looks", f"{peeking['naive_peeking_fpr']:.0%}")
c1.metric("mSPRT, 100 looks", f"{peeking['msprt_fpr']:.0%}")
c2.image(str(RESULTS / "peeking.png"))
