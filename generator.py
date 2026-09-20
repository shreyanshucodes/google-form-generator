from __future__ import annotations

import random
from datetime import date, timedelta

from form import FormField


FIRST_NAMES = [
    "Aarav", "Aanya", "Aditya", "Anaya", "Arjun", "Diya", "Ishaan", "Isha",
    "Kabir", "Kiara", "Krish", "Meera", "Nisha", "Neha", "Rohan", "Riya",
    "Samar", "Sara", "Shaurya", "Tanya", "Vihaan", "Vivaan", "Yash", "Zoya",
    "Dev", "Kavya", "Manav", "Myra", "Nakul", "Palak", "Reyansh", "Simran",
]
LAST_NAMES = [
    "Sharma", "Singh", "Gupta", "Patel", "Khan", "Verma", "Joshi", "Rao",
    "Mehta", "Malhotra", "Kapoor", "Chopra", "Bansal", "Nair", "Iyer", "Das",
    "Jain", "Saxena", "Mishra", "Sinha", "Agarwal", "Chauhan", "Shah", "Menon",
    "Kulkarni", "Desai", "Ghosh", "Reddy", "Pillai", "Banerjee", "Dutta", "Yadav",
]
CITIES = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Jaipur", "Lucknow", "Kolkata"]
OPINIONS = [
    "I usually check the reviews first.",
    "Discounts definitely get my attention.",
    "I notice reels more than normal ads.",
    "Good reviews make me trust a brand more.",
    "Too many ads just make me skip it.",
    "I like seeing the product being used.",
    "Recommendations from friends matter more to me.",
    "Influencers help me discover products sometimes.",
    "Clear prices and real reviews would help.",
    "It works better when the ad feels genuine.",
]
NAME_POOL = [f"{first} {last}" for first in FIRST_NAMES for last in LAST_NAMES]
random.Random(7919).shuffle(NAME_POOL)


def _name_for(index: int) -> str:
    return NAME_POOL[(index - 1) % len(NAME_POOL)]


def _text_for(field: FormField, index: int, rng: random.Random, profile: dict[str, str]) -> str:
    label = field.label.lower()
    first, last = _name_for(index).split()
    if "email" in label or field.name == "emailAddress":
        return f"{first.lower()}.{last.lower()}{index}@example.com"
    if "name" in label:
        return _name_for(index)
    if "phone" in label or "mobile" in label:
        return f"9{rng.randint(100000000, 999999999)}"
    if "city" in label or "location" in label:
        return rng.choice(CITIES)
    if "age" in label:
        return profile["age"]
    if "date" in label:
        return (date.today() - timedelta(days=rng.randint(0, 365))).isoformat()
    if "rating" in label or "score" in label:
        return str(rng.randint(1, 5))
    if "yes" in label or "agree" in label or "consent" in label:
        return rng.choice(["Yes", "No"])
    return OPINIONS[(index - 1) % len(OPINIONS)]


def _choose_age(options: list[str], rng: random.Random) -> str:
    """Choose from the form's age brackets, keeping the output realistic."""
    preferred = [option for option in options if any(char.isdigit() for char in option)]
    return rng.choice(preferred or options)


def _choose_occupation(options: list[str], age: str, rng: random.Random) -> str:
    normalized = {option.lower(): option for option in options}
    student = normalized.get("student")
    working = normalized.get("working professional")
    self_employed = normalized.get("self-employed")

    first_age = int(next((part for part in age.split() if part.isdigit()), "18"))
    if first_age < 21:
        choices = [option for option in (student, working) if option]
        weights = [0.85, 0.15][:len(choices)]
    else:
        choices = [option for option in (student, working, self_employed) if option]
        weights = [0.20, 0.55, 0.25][:len(choices)]
    return rng.choices(choices or options, weights=weights or None, k=1)[0]


def _store_answer(field: FormField, profile: dict[str, str], rng: random.Random) -> str | None:
    """Generate a coherent small-store operations profile when applicable."""
    label = field.label.lower()
    if not field.options:
        return None

    def choose(*weights: float) -> str:
        if len(weights) != len(field.options):
            return rng.choice(field.options)
        return rng.choices(field.options, weights=list(weights), k=1)[0]

    if "geographical location" in label:
        return choose(0.25, 0.25, 0.25, 0.25)
    if "business operation" in label:
        answer = choose(0.45, 0.40, 0.15)
        profile["years"] = answer
        return answer
    if "floor space" in label:
        years = profile.get("years", "")
        if "More than" in years:
            return choose(0.10, 0.45, 0.45)
        if "5 to" in years:
            return choose(0.25, 0.55, 0.20)
        return choose(0.60, 0.35, 0.05)
    if "total staff" in label or "employees" in label:
        floor = profile.get("floor", "")
        if "Large" in floor:
            answer = choose(0.05, 0.30, 0.65)
        elif "Medium" in floor:
            answer = choose(0.25, 0.55, 0.20)
        else:
            answer = choose(0.70, 0.25, 0.05)
        profile["staff"] = answer
        return answer
    if "delivery orders" in label:
        staff = profile.get("staff", "")
        floor = profile.get("floor", "")
        if "5 or more" in staff or "Large" in floor:
            answer = choose(0.15, 0.50, 0.35)
        elif "3–4" in staff or "Medium" in floor:
            answer = choose(0.45, 0.45, 0.10)
        else:
            answer = choose(0.75, 0.23, 0.02)
        profile["orders"] = answer
        return answer
    if "primary channel" in label:
        answer = choose(0.25, 0.35, 0.25, 0.15)
        profile["channel"] = answer
        return answer
    if "executes home deliveries" in label:
        staff = profile.get("staff", "")
        orders = profile.get("orders", "")
        if "5 or more" in staff or "Above 40" in orders:
            return field.options[0]
        if "3–4" in staff or "15 to 40" in orders:
            return field.options[1]
        return field.options[2]
    if "delivery radius" in label:
        orders = profile.get("orders", "")
        if "Above 40" in orders:
            return choose(0.15, 0.45, 0.40)
        if "15 to 40" in orders:
            return choose(0.35, 0.50, 0.15)
        return choose(0.65, 0.30, 0.05)
    if "free home delivery" in label or "minimum order" in label:
        orders = profile.get("orders", "")
        if "Above 40" in orders:
            return choose(0.15, 0.55, 0.30)
        if "15 to 40" in orders:
            return choose(0.25, 0.60, 0.15)
        return choose(0.45, 0.45, 0.10)
    if "operational bottleneck" in label:
        channel = profile.get("channel", "").lower()
        orders = profile.get("orders", "")
        if "whatsapp" in channel:
            return field.options[0] if rng.random() < 0.45 else field.options[3]
        if "Above 40" in orders:
            return field.options[0] if rng.random() < 0.55 else field.options[3]
        return rng.choice(field.options[1:])
    return None


def generate_row(fields: list[FormField], index: int, rng: random.Random) -> dict[str, object]:
    row: dict[str, object] = {}
    profile: dict[str, str] = {}
    for field in fields:
        label = field.label.lower()
        store_answer = _store_answer(field, profile, rng)
        if store_answer is not None:
            row[field.name] = store_answer
            if "floor space" in label:
                profile["floor"] = store_answer
            continue
        if "age" in label and field.options:
            profile["age"] = _choose_age(field.options, rng)
            row[field.name] = profile["age"]
            continue
        if "occupation" in label and field.options:
            row[field.name] = _choose_occupation(field.options, profile.get("age", "18"), rng)
            continue
        if field.options:
            if field.kind == "checkbox":
                count = min(len(field.options), rng.randint(1, 2))
                row[field.name] = rng.sample(field.options, count)
            else:
                row[field.name] = rng.choice(field.options)
        else:
            row[field.name] = _text_for(field, index, rng, profile)
    return row
