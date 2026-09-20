# Google Form Generator

Generate synthetic responses from a Google Form schema for a college data-science project.

The default workflow is safe and local: inspect the form, generate rows, and export CSV/JSON for analysis. Real submissions are opt-in with `--submit` and should only be used for a form you own or have permission to test.

## Setup

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Generate 100 rows

```text
python main.py "https://docs.google.com/forms/d/e/FORM_ID/viewform" --count 100 --output output/responses.csv
```

This also writes a JSON copy beside the CSV and prints the detected fields.

## Inspect only

```text
python main.py "FORM_URL" --inspect-only
```

## Submit test responses

Only use this with explicit permission from the form owner:

```text
python main.py "FORM_URL" --count 100 --submit --delay 1.0
```

The generator supports text, email, number, date, dropdown, radio, checkbox, and yes/no-style fields. For unusual questions, add a keyword or explicit option in `generator.py`.
