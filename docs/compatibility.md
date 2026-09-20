# Google Forms Compatibility

Google Forms renders modern forms from an embedded schema rather than ordinary
HTML input fields. This project reads that schema and supports common public,
single-path forms.

## Supported

- Text and paragraph responses
- Radio, dropdown, checkbox, and linear-scale answers
- Sectioned forms with a linear page path
- UTF-8 labels and options, including symbols such as `₹`
- CSV and JSON export for any successfully inspected form

## Submission Notes

Submission is opt-in. For an authorized live test, the form must permit public
responses and the generated data must be appropriate for the intended study.

The submitter sends:

- The inner answer-entry IDs from Google's schema
- Exact option text as published by the form
- The section page history expected by multi-page forms
- Hidden form session values required by Google Forms

## Not Supported Yet

- File uploads
- Sign-in-only forms and enforced email collection
- Branching paths that depend on answers
- Forms that require CAPTCHA or other interactive verification

If a form is unusual, begin with `--inspect-only`, generate locally, and
validate the output before considering any authorized submission.
