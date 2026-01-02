#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

source .venv/bin/activate

yamllint .
pymarkdown --config .pymarkdown.json scan .
ruff check .
pyright .
if rg -n --glob '*.py' '__all__' src; then
  echo "Found __all__ usage in src; remove it to satisfy visibility checks."
  exit 1
fi
