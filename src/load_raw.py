from pathlib import Path
import time
import pandas as pd
from sqlalchemy import text
from db import get_engine

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

def table_name(csv: Path) -> str:
    return csv.stem.replace("olist_", "").replace("_dataset", "")

def main():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
    for csv in sorted(RAW_DIR.glob("*.csv")):
        start = time.time()
        df = pd.read_csv(csv, dtype=str, keep_default_na=False)
        df["_source_file"] = csv.name
        df["_loaded_at"] = pd.Timestamp.now().isoformat()
        name = table_name(csv)
        df.to_sql(name, engine, schema="raw", if_exists="replace",
                  index=False, chunksize=1_000, method="multi")
        print(f"raw.{name:40s} {len(df):>9,} rows  {time.time()-start:5.1f}s")

if __name__ == "__main__":
    main()