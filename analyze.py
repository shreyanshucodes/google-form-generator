from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a quick summary of generated form data")
    parser.add_argument("csv_path", nargs="?", default="output/responses.csv")
    args = parser.parse_args()

    path = Path(args.csv_path)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("The CSV has no rows.")

    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(rows[0])}")
    for column in rows[0]:
        values = [row[column] for row in rows]
        missing = sum(not value.strip() for value in values)
        common = Counter(values).most_common(3)
        print(f"\n{column}")
        print(f"  Missing: {missing}")
        print(f"  Top values: {common}")


if __name__ == "__main__":
    main()
