import sys
from sqlalchemy import text
from db import get_engine


def load_batch(batch_date: str) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM stage.orders WHERE _batch_date = :d"), {"d": batch_date}
        )
        result = conn.execute(
            text("""
            INSERT INTO stage.orders
            SELECT *, CAST(:d AS date)
            FROM raw.orders
            WHERE left(order_purchase_timestamp, 10)::date = CAST(:d AS date)
        """),
            {"d": batch_date},
        )
        return result.rowcount


if __name__ == "__main__":
    d = sys.argv[1]
    print(f"{d}: loaded {load_batch(d)} orders")
