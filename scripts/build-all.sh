#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
TOOLS=()
BASES=()

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

load_env_file() {
  if [[ -f "${ENV_FILE}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${ENV_FILE}"
    set +a
  fi
}

split_list() {
  local raw="$1"
  local -n out=$2
  read -r -a out <<< "${raw}"
}

init_supported_lists() {
  split_list "${AICAGE_TOOLS}" TOOLS
  split_list "${AICAGE_BASES}" BASES
  [[ ${#TOOLS[@]} -gt 0 ]] || die "AICAGE_TOOLS is empty; update ${ENV_FILE}."
  [[ ${#BASES[@]} -gt 0 ]] || die "AICAGE_BASES is empty; update ${ENV_FILE}."
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
fi

load_env_file
init_supported_lists

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
  split_list "${platform_override}" platforms
  echo "[build-all] Building platform ${platforms[*]}." >&2
elif [[ -n "${AICAGE_PLATFORMS:-${PLATFORMS:-}}" ]]; then
  split_list "${AICAGE_PLATFORMS:-${PLATFORMS:-}}" platforms
  echo "[build-all] Building platforms ${platforms[*]} (from env)." >&2
else
  default_platforms=("linux/amd64" "linux/arm64")
  for p in "${default_platforms[@]}"; do
    if [[ "${p}" != "${host_platform}" ]]; then
      platforms+=("${p}")
    fi
  done
  platforms+=("${host_platform}")
  echo "[build-all] Building platforms ${platforms[*]} (host last)." >&2
fi

platform_arg=(--platform "${platforms[*]}")

for tool in "${TOOLS[@]}"; do
  for base in "${BASES[@]}"; do
    local_platforms="${platforms[*]}"
    echo "[build-all] Building ${tool}-${base} (platforms: ${local_platforms})" >&2
    "${ROOT_DIR}/scripts/build.sh" "${tool}" "${base}" "${platform_arg[@]}"
  done
done
