#!/usr/bin/env bash
set -euo pipefail

# Install Antigravity CLI using the official installer.
curl \
  -fsSL \
  --retry 8 \
  --retry-all-errors \
  --retry-delay 2 \
  --max-time 300 \
  https://antigravity.google/cli/install.sh | \
  bash

# Ensure the binary is on the global PATH for the runtime user.
if [[ -x "/root/.local/bin/agy" ]]; then
  install -m 0755 /root/.local/bin/agy /usr/local/bin/agy
elif command -v agy >/dev/null 2>&1; then
  # Fallback: copy whatever the installer placed on PATH.
  install -m 0755 "$(command -v agy)" /usr/local/bin/agy
fi

if ! command -v agy >/dev/null 2>&1; then
  echo "[install_agy] 'agy' executable not found after installation." >&2
  exit 1
fi
