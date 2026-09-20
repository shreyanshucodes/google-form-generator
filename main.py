from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests

from form import FormField, inspect_form
from generator import generate_row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic Google Form responses")
    parser.add_argument("url", help="Google Form viewform URL")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", default="output/responses.csv")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument("--submit", action="store_true", help="Submit generated rows; use only with permission")
    parser.add_argument("--delay", type=float, default=1.0)
    return parser.parse_args()


def flatten(row: dict[str, object]) -> dict[str, str]:
    return {key: ", ".join(value) if isinstance(value, list) else str(value) for key, value in row.items()}


def write_exports(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    flat_rows = [flatten(row) for row in rows]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat_rows[0]))
        writer.writeheader()
        writer.writerows(flat_rows)
    output.with_suffix(".json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


def print_schema(fields: list[FormField]) -> None:
    print(f"Detected {len(fields)} fields:")
    for field in fields:
        options = f" | options: {', '.join(field.options)}" if field.options else ""
        print(f"- {field.name}: {field.kind} | {field.label}{options}")


def submit_rows(url: str, rows: list[dict[str, object]], delay: float) -> None:
    print(f"Submitting {len(rows)} rows to {url}")
    view_url = urlunsplit((*urlsplit(url)[:2], urlsplit(url).path.replace("/formResponse", "/viewform"), "", ""))
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0", "Referer": view_url}
    form_page = session.get(view_url, headers=headers, timeout=20)
    form_page.raise_for_status()
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(form_page.text, "html.parser")
    hidden = {
        element.get("name"): element.get("value", "")
        for element in soup.select("input[type=hidden][name]")
        if element.get("name") in {"fvv", "partialResponse", "pageHistory", "fbzx", "submissionTimestamp"}
    }
    submit_url = urlunsplit((*urlsplit(url)[:2], urlsplit(url).path, "", ""))
    for index, row in enumerate(rows, start=1):
        payload: list[tuple[str, str]] = list(hidden.items())
        for key, value in row.items():
            values = value if isinstance(value, list) else [value]
            payload.extend((key, str(item)) for item in values)
        response = session.post(submit_url, data=payload, headers=headers, timeout=20)
        response.raise_for_status()
        print(f"Submitted {index}/{len(rows)}")
        if index != len(rows):
            time.sleep(delay)


def main() -> None:
    args = parse_args()
    if args.count < 1 or args.count > 10000:
        raise SystemExit("--count must be between 1 and 10000")
    response_url, fields = inspect_form(args.url)
    print_schema(fields)
    if args.inspect_only:
        return

    import random

    rng = random.Random(args.seed)
    rows = [generate_row(fields, index, rng) for index in range(1, args.count + 1)]
    output = Path(args.output)
    write_exports(rows, output)
    print(f"Wrote {output} and {output.with_suffix('.json')}")
    if args.submit:
        submit_rows(response_url, rows, args.delay)
    else:
        print("Dry run only. Use --submit only when you have permission to test the form.")


if __name__ == "__main__":
    main()
