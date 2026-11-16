# deposit-nudge-experiment

## Goal
End-to-end A/B test readout. Hillstrom email experiment framed as a fintech
deposit-match promo: conversion = account funded, spend = deposit amount.
Arms: Mens E-Mail, Womens E-Mail, No E-Mail (control).

## Stack
uv, DuckDB, dbt-duckdb, pandas, matplotlib, scipy, statsmodels, scikit-learn, scikit-uplift, pytest.

## Structure
- data/raw/            raw CSV (gitignored)
- dbt/                 staging -> fct_assignments -> fct_experiment_metrics
- src/abkit/           reusable stats: power, srm, ztest, welch, bootstrap, cuped, delta_method, msprt, uplift
- tests/               pytest for every abkit function, using known-answer cases
- docs/                experiment_brief.md, readout.md
- results/             numbers and charts
- scripts/             load, power, analysis, peeking, uplift
- run.py               runs those steps

## Rules
- Pure functions in src/abkit with type hints and docstrings.
- Every stats function gets a test against a hand-computed or simulated answer.
- Don't look at outcome metrics before docs/experiment_brief.md is committed.
- Run `uv run python run.py test` before every commit. Use conventional commit messages.
