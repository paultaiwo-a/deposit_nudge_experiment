.PHONY: data dbt test lint readout all

data:
	uv run python scripts/load_data.py

dbt:
	cd dbt && uv run dbt build --profiles-dir .

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

readout:
	uv run python scripts/run_analysis.py
	uv run python scripts/peeking_simulation.py

all: data dbt test readout
