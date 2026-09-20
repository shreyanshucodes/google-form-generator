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
CSR_SUGGESTIONS = [
    "Share regular updates with clear photos and results.",
    "Make the information easier to find on social media.",
    "Show how local communities benefit from the projects.",
    "Use simple videos to explain the work being done.",
    "Publish progress reports in an easy-to-understand way.",
    "Work with local people and show their feedback too.",
    "Give more details about the long-term environmental impact.",
    "Create more awareness through campus and community campaigns.",
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
    if "csr communication" in label or "improvement would you suggest" in label:
        return CSR_SUGGESTIONS[(index - 1) % len(CSR_SUGGESTIONS)]
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


def _csr_answer(field: FormField, profile: dict[str, str], rng: random.Random) -> str | None:
    """Generate a varied but internally consistent CSR-survey respondent."""
    label = field.label.lower()
    if not field.options:
        return None

    def choose(*weights: float) -> str:
        return rng.choices(field.options, weights=list(weights), k=1)[0]

    if label == "your age?":
        answer = choose(0.42, 0.30, 0.14, 0.10, 0.04)
        profile["csr_age"] = answer
        return answer
    if label == "your gender?":
        return choose(0.48, 0.48, 0.04)
    if label == "occupation?":
        age = profile.get("csr_age", "18 - 20")
        if age.startswith("18"):
            return choose(0.72, 0.13, 0.04, 0.03, 0.08)
        if age.startswith("21"):
            return choose(0.42, 0.28, 0.13, 0.09, 0.08)
        if age.startswith("24"):
            return choose(0.12, 0.40, 0.23, 0.17, 0.08)
        return choose(0.04, 0.35, 0.29, 0.24, 0.08)
    if "heard of reliance industries" in label:
        answer = choose(0.82, 0.18)
        profile["reliance_awareness"] = answer
        return answer
    if "jamnagar mango orchard" in label:
        answer = choose(0.38, 0.62) if profile.get("reliance_awareness") == "Yes" else choose(0.07, 0.93)
        profile["orchard_awareness"] = answer
        return answer
    if "create both social/environmental value" in label:
        return choose(0.82, 0.04, 0.14)
    if "overall perception of reliance" in label:
        if profile.get("reliance_awareness") == "No":
            return choose(0.10, 0.08, 0.82)
        return choose(0.60, 0.10, 0.30)
    if "csr activities" in label:
        return choose(0.04, 0.09, 0.24, 0.42, 0.21)
    if "environmental sustainability" in label:
        return choose(0.02, 0.06, 0.14, 0.43, 0.35)
    if "tree plantation" in label or "treated industrial" in label:
        return choose(0.03, 0.08, 0.19, 0.45, 0.25)
    if "brand image" in label or "increase trust" in label or "differentiate" in label:
        return choose(0.04, 0.10, 0.27, 0.40, 0.19)
    if "long-term environmental responsibility" in label:
        return choose(0.02, 0.06, 0.15, 0.44, 0.33)
    return None


def generate_row(fields: list[FormField], index: int, rng: random.Random) -> dict[str, object]:
    row: dict[str, object] = {}
    profile: dict[str, str] = {}
    for field in fields:
        label = field.label.lower()
        csr_answer = _csr_answer(field, profile, rng)
        if csr_answer is not None:
            row[field.name] = csr_answer
            continue
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
