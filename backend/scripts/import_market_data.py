import argparse
import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Import market prices CSV into SQLite")
    parser.add_argument("--db", required=True, help="SQLite database path")
    parser.add_argument("--csv", required=True, help="Input CSV path")
    parser.add_argument("--source", default="manual_import", help="Data source name")
    return parser.parse_args()


def main():
    args = parse_args()
    db_path = Path(args.db).resolve()
    csv_path = Path(args.csv).resolve()

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    conn = sqlite3.connect(db_path)
    try:
        inserted = 0
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conn.execute(
                    """
                    INSERT INTO market_prices (
                        province_code, market_date, timeslot, price, source, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["province_code"].upper(),
                        row["market_date"],
                        row["timeslot"],
                        float(row["price"]),
                        args.source,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                inserted += 1
        conn.commit()
        print(f"Imported rows: {inserted}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
