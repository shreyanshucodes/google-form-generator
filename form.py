from __future__ import annotations

import json
import re
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
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0 (compatible; form-generator/1.0)"},
    )
    response.raise_for_status()
    # Google Forms serves UTF-8 text but may omit a reliable charset header.
    # Decode the embedded schema explicitly so option values remain exact.
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    schema_fields = _schema_fields(response.text)
    if schema_fields:
        return response_url(response.url), schema_fields

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


def _schema_fields(html: str) -> list[FormField]:
    """Read modern Google Forms fields from FB_PUBLIC_LOAD_DATA_."""
    match = re.search(r"var FB_PUBLIC_LOAD_DATA_ = (.*?);</script>", html, re.S)
    if not match:
        return []

    try:
        payload = json.loads(match.group(1))
        questions = payload[1][1]
    except (IndexError, TypeError, json.JSONDecodeError):
        return []

    fields: list[FormField] = []
    for question in questions:
        if not isinstance(question, list) or len(question) < 4:
            continue
        question_id, label, question_type = question[0], question[1], question[3]
        if question_type in {6, 8}:  # section headers
            continue

        answer_config = question[4] if len(question) > 4 else None
        if question_type == 7 and isinstance(answer_config, list):  # grid
            for row in answer_config:
                if not isinstance(row, list) or len(row) < 4:
                    continue
                row_id, option_data, row_label = row[0], row[1], row[3]
                options = _options(option_data)
                fields.append(
                    FormField(
                        name=f"entry.{question_id}.{row_id}",
                        kind="radio",
                        label=str(row_label[0]) if row_label else str(label),
                        options=options,
                    )
                )
            continue

        options = _options(answer_config[0][1] if answer_config else None)
        kind = {0: "text", 1: "textarea", 2: "radio", 4: "checkbox", 5: "scale"}.get(
            question_type, "text"
        )
        # The outer ID identifies the question; Google's POST field uses the
        # inner answer ID from the answer configuration.
        answer_id = answer_config[0][0] if answer_config else question_id
        fields.append(FormField(f"entry.{answer_id}", kind, str(label), options))

    return fields


def _options(option_data) -> list[str]:
    if not isinstance(option_data, list):
        return []
    result: list[str] = []
    for option in option_data:
        value = option[0] if isinstance(option, list) and option else option
        if isinstance(value, str) and value and value not in result:
            result.append(value)
    return result


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
