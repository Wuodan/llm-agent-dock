# Subtask 3 Summary: Base Selection Description

## Outcome

Subtask 3 is implemented: base descriptions from release images metadata are shown during base selection prompts.

## Key changes

- Base selection prompts now render `base: description` using metadata in `src/aicage/runtime/prompts.py`.
- Base selection request carries tool, context, and tool metadata to keep prompt formatting encapsulated.
- Prompt tests updated in `tests/aicage/runtime/test_prompts.py`.

## Tests run

- `yamllint .`
- `ruff check .`
- `pymarkdown --config .pymarkdown.json scan .`
- `pytest --cov=src --cov-report=term-missing`
