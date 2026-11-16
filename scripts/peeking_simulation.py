"""Simulate A/A tests to compare false positives from naive peeking vs mSPRT."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from abkit import always_valid_pvalues

OUT = Path("results")
SIMS = 2000
N_MAX = 10_000
PEEK_EVERY = 100
ALPHA = 0.05
TAU2 = 0.01
SEED = 0


def simulate() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Cumulative share of A/A tests rejected by each look, for naive z-test and mSPRT."""
    rng = np.random.default_rng(SEED)
    n = np.arange(PEEK_EVERY, N_MAX + 1, PEEK_EVERY)
    naive = np.zeros((SIMS, len(n)), dtype=bool)
    msprt = np.zeros((SIMS, len(n)), dtype=bool)
    for s in range(SIMS):
        t = rng.normal(0, 1, N_MAX).cumsum()[n - 1]
        c = rng.normal(0, 1, N_MAX).cumsum()[n - 1]
        diff, var = (t - c) / n, 2 / n
        p_naive = 2 * stats.norm.sf(np.abs(diff) / np.sqrt(var))
        naive[s] = np.logical_or.accumulate(p_naive < ALPHA)
        msprt[s] = always_valid_pvalues(diff, var, TAU2) < ALPHA
    return n, naive.mean(axis=0), msprt.mean(axis=0)


def chart(n: np.ndarray, naive: np.ndarray, msprt: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(n, naive * 100, marker=".", label="Z-test, checked along the way")
    ax.plot(n, msprt * 100, marker=".", label="mSPRT, checked along the way")
    ax.axhline(ALPHA * 100, linestyle="--", color="black", label="5% line")
    ax.set_xlabel("Users per group")
    ax.set_ylabel("False positive rate (%)")
    ax.set_title("False Positives from Checking the Test Early")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig


def main() -> None:
    n, naive, msprt = simulate()
    single_look = float(naive[0])
    summary = {
        "simulations": SIMS,
        "looks": len(n),
        "tau2": TAU2,
        "single_look_fpr": single_look,
        "naive_peeking_fpr": float(naive[-1]),
        "msprt_fpr": float(msprt[-1]),
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "peeking.json").write_text(json.dumps(summary, indent=2))
    chart(n, naive, msprt).savefig(OUT / "peeking.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
