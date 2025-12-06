#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS=(cline codex droid)
BASES=(act ubuntu)

usage() {
  cat <<'USAGE'
Usage: scripts/build-all.sh [build-options]

Builds the full matrix of <tool>-<base> combinations. Any options after the script name are
forwarded to scripts/build.sh for each build (e.g., --platform, --load, --no-cache,
--print).
USAGE
  exit 1
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
fi

extra_args=("$@")

for tool in "${TOOLS[@]}"; do
  for base in "${BASES[@]}"; do
    echo "[build-all] Building ${tool}-${base}" >&2
    "${ROOT_DIR}/scripts/build.sh" "${tool}" "${base}" "${extra_args[@]}"
  done
done
