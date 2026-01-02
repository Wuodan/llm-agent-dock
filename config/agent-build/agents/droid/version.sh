#!/usr/bin/env bash
set -euo pipefail

installer="$(mktemp)"
curl -fsSL https://app.factory.ai/cli -o "${installer}"
version="$(grep -E '^VER="[^"]+"' "${installer}" | sed -E 's/^VER="([^"]+)".*/\1/')"
rm -f "${installer}"

if [[ -z "${version}" ]]; then
  echo "[version_droid] Failed to parse version from installer." >&2
  exit 1
fi

echo "${version}"
