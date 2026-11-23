import time, uuid
from datetime import datetime
from pathlib import Path
import yaml
from sqlalchemy import text
from db import get_engine

RULES = Path(__file__).resolve().parents[1] / "config" / "rules.yaml"

DDL = """
CREATE SCHEMA IF NOT EXISTS audit;
CREATE TABLE IF NOT EXISTS audit.check_results (
  run_id       text,
  run_ts       timestamp,
  rule_id      text,
  table_name   text,
  dimension    text,
  severity     text,
  rows_checked bigint,
  rows_failed  bigint,
  pass_rate    numeric(7,4),
  status       text,
  duration_s   numeric(8,2)
);
"""


def main():
    rules = yaml.safe_load(RULES.read_text())["rules"]
    engine = get_engine()
    run_id, run_ts = uuid.uuid4().hex[:8], datetime.now()
    with engine.begin() as conn:
        conn.execute(text(DDL))
        for r in rules:
            start = time.time()
            checked = conn.execute(text(f"SELECT count(*) FROM {r['table']}")).scalar()
            failed = conn.execute(text(f"SELECT count(*) FROM ({r['sql']}) f")).scalar()
            rate = 1 - failed / checked if checked else 1
            status = "pass" if failed == 0 else r["severity"]
            conn.execute(
                text("""
                INSERT INTO audit.check_results VALUES
                (:run_id, :run_ts, :rule_id, :tbl, :dim, :sev, :chk, :fail, :rate, :status, :dur)
            """),
                dict(
                    run_id=run_id,
                    run_ts=run_ts,
                    rule_id=r["id"],
                    tbl=r["table"],
                    dim=r["dimension"],
                    sev=r["severity"],
                    chk=checked,
                    fail=failed,
                    rate=rate,
                    status=status,
                    dur=time.time() - start,
                ),
            )
            print(f"{status:5s} {r['id']:40s} {failed:>6,} / {checked:,}")
    print(f"run {run_id} done")


if __name__ == "__main__":
    main()
