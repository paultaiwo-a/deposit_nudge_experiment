"""T-learner uplift model per creative, evaluated with Qini and uplift@k on a holdout."""

import json
import warnings
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklift.metrics import qini_auc_score, qini_curve, uplift_at_k

from abkit import t_learner_uplift

warnings.filterwarnings("ignore", category=FutureWarning)

DB_PATH = "warehouse.duckdb"
OUT = Path("results")
ARMS = {"mens_email": "Mens E-Mail", "womens_email": "Womens E-Mail"}
ARM_COLORS = {"mens_email": "#2a78d6", "womens_email": "#eb6834"}
SEGMENTS = ["channel", "zip_code", "newbie", "history_segment", "bought_mens", "bought_womens"]
FEATURES = ["recency", "pre_deposits", "bought_mens", "bought_womens", "newbie"]
CATEGORICAL = ["zip_code", "channel"]
K = 0.3
SEED = 0


def load() -> pd.DataFrame:
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.sql(
            """
            select a.*, m.funded
            from fct_assignments a
            join fct_experiment_metrics m using (user_id)
            """
        ).df()


def features(df: pd.DataFrame) -> np.ndarray:
    return pd.get_dummies(df[FEATURES + CATEGORICAL], columns=CATEGORICAL, dtype=float).to_numpy()


def observed_uplift(df: pd.DataFrame) -> float:
    return df.loc[df.treated, "funded"].mean() - df.loc[~df.treated, "funded"].mean()


def segment_table(test: pd.DataFrame) -> list[dict]:
    rows = []
    for col in SEGMENTS:
        for value, g in test.groupby(col):
            rows.append(
                {
                    "segment": f"{col} = {value}",
                    "users": len(g),
                    "predicted_uplift": g.uplift.mean(),
                    "observed_uplift": observed_uplift(g),
                }
            )
    return sorted(rows, key=lambda r: r["predicted_uplift"], reverse=True)


def run_arm(df: pd.DataFrame, arm: str) -> tuple[dict, pd.DataFrame]:
    d = df[df.arm.isin([arm, "control"])].copy()
    d["treated"] = d.arm == arm
    X = features(d)
    idx_train, idx_test = train_test_split(
        np.arange(len(d)), test_size=0.3, random_state=SEED, stratify=d.treated * 2 + d.funded
    )
    train, test = d.iloc[idx_train], d.iloc[idx_test].copy()
    model = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, random_state=SEED)
    test["uplift"] = t_learner_uplift(
        model, X[idx_train], train.funded.to_numpy(), train.treated.to_numpy(), X[idx_test]
    )
    y, s, t = test.funded.to_numpy(), test.uplift.to_numpy(), test.treated.to_numpy()
    summary = {
        "qini_auc": qini_auc_score(y, s, t),
        "uplift_at_30pct": uplift_at_k(y, s, t, strategy="overall", k=K),
        "average_uplift": observed_uplift(test),
        "segments": segment_table(test),
    }
    return summary, test


def qini_chart(tests: dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for arm, test in tests.items():
        x, y = qini_curve(test.funded, test.uplift, test.treated)
        ax.plot(x / x[-1], y, color=ARM_COLORS[arm], linewidth=2, label=f"{ARMS[arm]} model")
        ax.plot([0, 1], [0, y[-1]], color=ARM_COLORS[arm], linestyle="--", linewidth=1)
    ax.set_xlabel("Share of users targeted, highest predicted uplift first")
    ax.set_ylabel("Incremental funded accounts")
    ax.set_title("Qini curve on holdout (dashed = random targeting)")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def main() -> None:
    df = load()
    results, tests = {}, {}
    for arm in ARMS:
        results[arm], tests[arm] = run_arm(df, arm)

    OUT.mkdir(exist_ok=True)
    (OUT / "uplift.json").write_text(json.dumps(results, indent=2))
    qini_chart(tests).savefig(OUT / "qini.png", dpi=150)
    for arm, r in results.items():
        print(f"{ARMS[arm]}: qini auc {r['qini_auc']:.4f}, uplift@30% {r['uplift_at_30pct']:.4f}")
        for s in r["segments"][:5]:
            print(f"  {s['segment']:28s} {s['predicted_uplift']:+.4f} {s['observed_uplift']:+.4f}")


if __name__ == "__main__":
    main()
