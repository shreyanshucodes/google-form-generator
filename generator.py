from __future__ import annotations

import random
from datetime import date, timedelta

from form import FormField


FIRST_NAMES = ["Aarav", "Aanya", "Kabir", "Meera", "Rohan", "Isha", "Vivaan", "Anaya"]
LAST_NAMES = ["Sharma", "Singh", "Gupta", "Patel", "Khan", "Verma", "Joshi", "Rao"]
CITIES = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Jaipur", "Lucknow", "Kolkata"]


def _text_for(field: FormField, index: int, rng: random.Random) -> str:
    label = field.label.lower()
    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    if "email" in label or field.name == "emailAddress":
        return f"{first.lower()}.{last.lower()}{index}@example.com"
    if "name" in label:
        return f"{first} {last}"
    if "phone" in label or "mobile" in label:
        return f"9{rng.randint(100000000, 999999999)}"
    if "city" in label or "location" in label:
        return rng.choice(CITIES)
    if "age" in label:
        return str(rng.randint(18, 30))
    if "date" in label:
        return (date.today() - timedelta(days=rng.randint(0, 365))).isoformat()
    if "rating" in label or "score" in label:
        return str(rng.randint(1, 5))
    if "yes" in label or "agree" in label or "consent" in label:
        return rng.choice(["Yes", "No"])
    return f"Synthetic response {index}"


def generate_row(fields: list[FormField], index: int, rng: random.Random) -> dict[str, object]:
    row: dict[str, object] = {}
    for field in fields:
        if field.options:
            if field.kind == "checkbox":
                count = min(len(field.options), rng.randint(1, 2))
                row[field.name] = rng.sample(field.options, count)
            else:
                row[field.name] = rng.choice(field.options)
        else:
            row[field.name] = _text_for(field, index, rng)
    return row
