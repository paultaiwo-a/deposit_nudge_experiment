# Readout: deposit-match nudge

Analysis follows the pre-registered plan in [experiment_brief.md](experiment_brief.md).
All numbers come from `results/*.json` and are rebuilt by `make all`.

## Decision

**Ship creative A (Mens E-Mail) to all eligible users.**

Both creatives passed every check in the decision rule. Creative A had the larger
funding-rate lift, so the rule picks A.

| Check | Creative A (Mens) | Creative B (Womens) |
|---|---|---|
| SRM, p >= 0.001 | p = 0.90, pass | pass |
| Funding lift > 0 and Holm p < 0.05 | Holm p = 3e-13, pass | Holm p = 0.0002, pass |
| Guardrail CI not entirely below -20% | [-20.2%, +19.4%], pass | [-13.8%, +27.6%], pass |

## Sample

| Arm | Users |
|---|---|
| Control | 21,306 |
| Creative A | 21,307 |
| Creative B | 21,387 |

No sample ratio mismatch (chi-square p = 0.90).

## Effect sizes (vs control, 95% CI)

Control baselines: funding rate 0.57%, visit rate 10.6%, deposit per user 0.65,
deposit per funded user 114.

| Metric | Creative A | Creative B |
|---|---|---|
| Funding rate (primary) | +0.68 pp [+0.50, +0.86], +119% | +0.31 pp [+0.15, +0.47], +54% |
| Visit rate | +7.7 pp [+7.0, +8.3], +72% | +4.5 pp [+3.9, +5.2], +43% |
| Deposit per user | +0.77 [+0.49, +1.05], +118% | +0.42 [+0.17, +0.68], +65% |
| Deposit per user, bootstrap CI | [+0.50, +1.05] | [+0.18, +0.69] |
| Deposit per user, CUPED | +0.77 [+0.48, +1.05] | +0.42 [+0.17, +0.68] |
| Deposit per funded user (guardrail) | -0.5 [-23.1, +22.1], -0.4% | +7.9 [-15.7, +31.5], +6.9% |

![Funding rate by arm](../results/funding_rate.png)
![Relative lift](../results/lift_chart.png)

## Business impact per 10,000 users messaged

| | Creative A | Creative B |
|---|---|---|
| Incremental funded accounts | 68 [50, 86] | 31 [15, 47] |
| Incremental deposits | 7,700 [4,800, 10,500] | 4,200 [1,700, 6,800] |

The lift comes from more people funding, not from larger deposits: deposit per funded
user is flat for both creatives.

## Targeting

A T-learner (gradient boosting, 70/30 split) was fit for each creative. This is
exploratory and does not change the decision.

| | Qini AUC | Uplift in top 30% | Average uplift |
|---|---|---|---|
| Creative A | -0.022 | +0.57 pp | +0.67 pp |
| Creative B | +0.085 | +0.66 pp | +0.31 pp |

- Creative A: the model does not beat random targeting. Send to everyone.
- Creative B: some signal. Users with more than $750 in prior-year deposits respond
  about 3 to 4 times more than average. Worth a follow-up test if B is ever reused.

![Qini curve](../results/qini.png)

## Caveats

1. **CUPED did not help.** Prior-year deposits correlate 0.02 with in-test deposits, so
   the CUPED interval is less than 0.1% narrower. A better covariate would be deposits in
   the weeks just before the test.
2. **Guardrail is weak.** Only about 120 to 270 users per arm funded an account, so the
   deposit-per-funded-user CI is about ±20%. Creative A's lower bound sits just below the
   -20% line. It passes the rule as written, but the data cannot rule out a drop of that size.
3. **Costs are not included.** Incremental deposits ignore the cost of the match. Net value
   needs the match rate and cap.
4. **Short window.** Outcomes cover two weeks. We do not know whether funded accounts stay
   active or whether the effect fades on repeat sends.
5. **Proxy data.** Hillstrom is a retail email test reframed as a deposit promo. The method
   carries over; the effect sizes should not be quoted as fintech benchmarks.
6. **Peeking.** This analysis used one fixed look. If the next test is monitored while
   it runs, use mSPRT: in simulation, checking a z-test 100 times gave a 39% false positive
   rate, against 3% for mSPRT (`results/peeking.png`).
