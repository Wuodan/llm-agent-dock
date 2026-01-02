# AI Agent Playbook

Audience: AI coding agents working in this repo and its submodules. Keep user-facing docs clean and
follow [DEVELOPMENT.md](DEVELOPMENT.md) for workflows.

## Ground rules

- Markdown: wrap near ~120 chars.
- Keep [README.md](README.md) user-only.
- Put build/process notes in [DEVELOPMENT.md](DEVELOPMENT.md).
- KISS: default to minimal changes; avoid optional parameters/configs or extra result objects unless explicitly requested.
- Avoid defensive checks for impossible states unless explicitly requested.
- Visibility first: new modules default to private (`_`); keep constants private unless used outside the module.
- Do not invent new public APIs or config fields unless explicitly requested.
- For all Python commands, use a virtualenv:  
  `python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt`.
- Keep code and docs free of conversational feedback to humans; only ship product-ready content.
- Disabling linters via comments (e.g., `# noqa`) is a last resort; analyze and fix first, and only
  add suppressions with explicit approval.

## General coding guidelines

I come from Java and greatly value `Clean Code` and `Separation/Encapsulation`.  
Meaning:
- I want to see datatypes explicitly.
- I want clean capsulation with private/public visibility. Default is always private and visibility is only increased
  when needed - for files, classes, methods, variables ... everywhere. If this is violated I stop my review immediately
  so get this right.
- pass wrapping objects when you can, don't split wrapping objects into variables
- Respect `doc/python-test-structure-guidelines.md` when it comes to writing Python tests.

## Visibility rules

- Defining scope: anything not used outside its defining scope must be prefixed with `_`.
- Module scope: functions, constants, and classes used outside their module must be public; if used only inside the
  module, prefix with `_`.
- Class scope: methods and attributes used outside their defining class must be public; if used only inside the class,
  prefix with `_`.
- Package scope: modules/files imported from outside the package must be public; if used only inside the package, prefix
  the filename with `_`.
- Tests are exempt from the "outside" checks above.

## Repo structure

- [README.md](README.md) (users)
- [DEVELOPMENT.md](DEVELOPMENT.md) (advanced users)
- [Why cage agents?](README.md#why-cage-agents) (rationale).
- Submodules:
  - `aicage-image-base/` builds base OS layers
  - `aicage-image/` builds final agent images
  - `aicage-image-util/` builds utility images for `aicage` runtime tasks

## Linting and tests

- Lint: `yamllint .`, `ruff check .`, `pymarkdown --config .pymarkdown.json scan .`
- Tests: `pytest --cov=src --cov-report=term-missing`
