#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS=(cline codex droid)
BASES=(act ubuntu)

die() {
  echo "[build-all] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: scripts/build-all.sh [build-options]

Builds the full matrix of <tool>-<base> combinations. Any options after the script name are
forwarded to scripts/build.sh for each build (e.g., --platform). By default all
platforms are built with the host architecture listed last.

Options:
  --platform <value>  Build only a single platform (e.g., linux/amd64)
  -h, --help      Show this help and exit
USAGE
  exit 1
}

detect_host_platform() {
  local arch
  arch="$(uname -m)"
  case "${arch}" in
    x86_64|amd64) echo "linux/amd64" ;;
    arm64|aarch64) echo "linux/arm64" ;;
    *) echo "linux/amd64" ;; # fallback
  esac
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
fi

host_platform="$(detect_host_platform)"
platform_override=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      [[ $# -ge 2 ]] || { echo "[build-all] --platform requires a value" >&2; exit 1; }
      platform_override="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      die "Unexpected argument '$1'"
      ;;
  esac
done

platforms=()
if [[ -n "${platform_override}" ]]; then
  platforms=("${platform_override}")
  echo "[build-all] Building platform ${platforms[0]}." >&2
else
  default_platforms=("linux/amd64" "linux/arm64")
  host_normalized="${host_platform}"
  for p in "${default_platforms[@]}"; do
    if [[ "${p}" != "${host_normalized}" ]]; then
      platforms+=("${p}")
    fi
  done
  platforms+=("${host_normalized}")
  echo "[build-all] Building platforms ${platforms[*]} (host last)." >&2
fi

platform_arg=(--platform "$(IFS=,; echo "${platforms[*]}")")

for tool in "${TOOLS[@]}"; do
  for base in "${BASES[@]}"; do
    local_platforms="${platforms[*]}"
    echo "[build-all] Building ${tool}-${base} (platforms: ${local_platforms})" >&2
    "${ROOT_DIR}/scripts/build.sh" "${tool}" "${base}" "${platform_arg[@]}"
  done
done
