### Deposit Match Email Test

##### Paul Taiwo-Adeyemo, November 2026

Two emails were tested against no email. The question is which one, if either, gets more customers to fund an account.

Send the men's email. The funding rate went from 0.57% to 1.25%. The rules are in [docs/experiment_brief.md](docs/experiment_brief.md). The numbers are in [docs/readout.md](docs/readout.md).

![Funding Rate by Group](results/funding_rate.png)

### How to Run

```bash
uv sync
uv run python run.py all
```

`python run.py all` loads the data, builds the tables, runs the tests, and writes the charts in `results/`.
