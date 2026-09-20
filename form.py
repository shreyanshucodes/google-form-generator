from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup


@dataclass
class FormField:
    name: str
    kind: str
    label: str
    options: list[str] = field(default_factory=list)


def response_url(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path.replace("/viewform", "/formResponse")
    if path.endswith("/form"):
        path += "Response"
    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def _label(element) -> str:
    parent = element.find_parent(["div", "label"])
    if not parent:
        return element.get("aria-label") or element.get("name") or "response"
    text = " ".join(parent.get_text(" ", strip=True).split())
    return text[:160] or element.get("aria-label") or element.get("name") or "response"


def inspect_form(url: str, timeout: int = 20) -> tuple[str, list[FormField]]:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    fields: dict[str, FormField] = {}

    for element in soup.select("input[name], textarea[name], select[name]"):
        name = element.get("name", "")
        if not name or not (name.startswith("entry.") or name == "emailAddress"):
            continue
        input_type = element.get("type", "text").lower()
        if input_type in {"hidden", "submit", "button", "file"}:
            continue
        kind = "text" if element.name == "textarea" else input_type
        if element.name == "select":
            kind = "select"
        current = fields.setdefault(name, FormField(name, kind, _label(element)))
        for option in element.select("option"):
            value = option.get("value") or option.get_text(" ", strip=True)
            if value and value not in current.options:
                current.options.append(value)

    for name, group in _choice_groups(soup).items():
        current = fields.setdefault(name, FormField(name, group["kind"], group["label"]))
        for value in group["options"]:
            if value not in current.options:
                current.options.append(value)

    return response_url(url), list(fields.values())


def _choice_groups(soup) -> dict[str, dict]:
    groups: dict[str, dict] = {}
    for element in soup.select("input[type=radio][name], input[type=checkbox][name]"):
        name = element["name"]
        group = groups.setdefault(name, {
            "kind": element.get("type", "radio"),
            "label": _label(element),
            "options": [],
        })
        value = element.get("value", "")
        if value and value not in group["options"]:
            group["options"].append(value)
    return groups
