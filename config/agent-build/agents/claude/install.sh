#!/usr/bin/env bash
set -euo pipefail

# Install Claude using the official installer.
curl -fsSL https://claude.ai/install.sh | bash

# Ensure the binary is on the global PATH for the runtime user.
if [[ -x "/root/.local/bin/claude" ]]; then
  install -m 0755 /root/.local/bin/claude /usr/local/bin/claude
elif command -v claude >/dev/null 2>&1; then
  # Fallback: copy whatever the installer placed on PATH.
  install -m 0755 "$(command -v claude)" /usr/local/bin/claude
fi

# Remove root-home artifacts left by the installer; the image uses /usr/local/bin.
rm -rf /root/.claude /root/.local/bin/claude /root/.local/share/claude

if ! command -v claude >/dev/null 2>&1; then
  echo "[install_claude] 'claude' executable not found after installation." >&2
  exit 1
fi
