.PHONY: data dbt test lint readout app all

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
	uv run python scripts/uplift.py

app:
	uv run streamlit run app/streamlit_app.py

all: data dbt test readout
