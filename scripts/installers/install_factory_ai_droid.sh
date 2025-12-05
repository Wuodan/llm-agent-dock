#!/usr/bin/env bash
set -euo pipefail

npm install -g @factory-ai/droid

if ! command -v droid >/dev/null; then
  echo "[install_factory_ai_droid] 'droid' executable not found after installation." >&2
  exit 1
fi
