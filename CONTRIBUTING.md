# Contributing

Thanks for improving Google Form Generator.

## Before You Change Code

1. Run `python -m unittest discover -s tests`.
2. Keep the default workflow local and export-focused.
3. Preserve exact Google Forms option values; small Unicode changes can make an
   answer invalid.
4. Add profile logic only when it makes generated rows more coherent.

## Pull Request Guidelines

- Keep changes focused.
- Explain the supported form behavior or survey profile you added.
- Include an offline test when parsing or generation logic changes.
- Do not commit generated response data from real forms.
