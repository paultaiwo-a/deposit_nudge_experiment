# Experiment brief: deposit-match nudge

Pre-registration. Written and committed before any treatment-arm outcome was examined.
Only control-arm baselines were used for the power analysis (`scripts/power_analysis.py`).

## Context

We send existing customers a deposit-match promo by email. Two creatives are tested
against a holdout:

| Arm | Hillstrom segment | Role |
|---|---|---|
| Control | No E-Mail | no message |
| Treatment A | Mens E-Mail | creative A |
| Treatment B | Womens E-Mail | creative B |

Data: Hillstrom MineThatData email experiment, about 64,000 users randomised in equal
proportions. Mapping: `conversion` = account funded, `spend` = deposit amount,
`visit` = app visit, `history` = prior-year deposits.

## Hypothesis

H1: Each creative increases the share of users who fund their account in the two weeks
after send, compared with no message.

H0: Funding rate is the same as control.

## Metrics

| Type | Metric | Definition | Test |
|---|---|---|---|
| Primary | Funding rate | funded users / users assigned | two-proportion z-test |
| Secondary | Deposit per user | total deposits / users assigned | Welch t-test, CUPED on `history`, bootstrap CI |
| Secondary | Visit rate | visiting users / users assigned | two-proportion z-test |
| Guardrail | Deposit per funded user | total deposits / funded users | delta method |
| Validity | Sample ratio | users per arm vs 1:1:1 | chi-square SRM check |

Analysis is intention-to-treat on all assigned users.

## Power and MDE

Control baselines: funding rate 0.573%, deposit per user 0.653 (sd 11.59).

Settings: two-sided alpha 0.05 split across two comparisons (0.025 each), power 80%,
about 21,000 users per arm.

| Metric | Minimum detectable effect |
|---|---|
| Funding rate | +0.25 pp absolute (+44% relative) |
| Deposit per user | +0.35 absolute (+53% relative) |

The test can only detect large lifts. Funding is rare, so a smaller real effect is
likely to come out non-significant. Deposit per user is very noisy, so CUPED on `history`
is pre-specified to reduce variance.

## Analysis plan

1. SRM check across all three arms. If p < 0.001, stop and investigate before reading results.
2. Each treatment vs control on every metric. No treatment-vs-treatment test for the decision.
3. Holm correction across the two primary comparisons. Secondary metrics are reported with
   unadjusted CIs and treated as supporting evidence.
4. Effect sizes reported as absolute and relative lift with 95% CIs.
5. Segment analysis (uplift model) is exploratory and does not change the decision.

## Decision rule

Ship a creative if all of these hold:

- SRM check passes (p >= 0.001).
- Funding-rate lift is positive and significant after Holm (adjusted p < 0.05).
- Guardrail: the 95% CI for deposit per funded user does not lie entirely below
  -20% relative to control.

If both creatives pass, ship the one with the larger funding-rate lift. If neither passes,
do not ship and keep the holdout.
