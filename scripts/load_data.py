"""Load the Hillstrom email experiment into DuckDB as raw_hillstrom."""

from pathlib import Path

import duckdb
import pandas as pd

RAW_DIR = Path("data/raw")
CSV_URL = (
    "http://www.minethatdata.com/"
    "Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
)
DB_PATH = "warehouse.duckdb"


def fetch() -> pd.DataFrame:
    try:
        from sklift.datasets import fetch_hillstrom

        d = fetch_hillstrom(target_col="all", data_home=str(RAW_DIR))
        return pd.concat([d.data, d.target, d.treatment], axis=1)
    except Exception as e:
        print(f"sklift fetch failed ({e}), falling back to CSV")
        path = RAW_DIR / "hillstrom.csv"
        if not path.exists():
            pd.read_csv(CSV_URL).to_csv(path, index=False)
        return pd.read_csv(path)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df = fetch()
    df.insert(0, "user_id", range(1, len(df) + 1))
    with duckdb.connect(DB_PATH) as con:
        con.execute("create or replace table raw_hillstrom as select * from df")
        n = con.execute("select count(*) from raw_hillstrom").fetchone()[0]
    print(f"loaded {n} rows into {DB_PATH}")


if __name__ == "__main__":
    main()
