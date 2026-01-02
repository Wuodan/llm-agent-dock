#!/usr/bin/env bash
set -euo pipefail

# Install Factory.ai Droid CLI using the official installer.
export HOME=/root

curl -fsSL https://app.factory.ai/cli | sh

# Ensure the binary is on the global PATH for the runtime user.
if [[ -x "/root/.local/bin/droid" ]]; then
  install -m 0755 /root/.local/bin/droid /usr/local/bin/droid
elif command -v droid >/dev/null 2>&1; then
  # Fallback: copy whatever the installer placed on PATH.
  install -m 0755 "$(command -v droid)" /usr/local/bin/droid
fi

if ! command -v droid >/dev/null 2>&1; then
  echo "[install_droid] 'droid' executable not found after installation." >&2
  exit 1
fi
