#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FINAL_DIR="${ROOT_DIR}/final-images"
TOOLS=()
BASES=()

die() {
  echo "[build-all] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: final-images/scripts/build-all.sh [build-options]

Builds the full matrix of <tool>-<base> combinations. Any options after the script name are
forwarded to final-images/scripts/build.sh for each build (e.g., --platform). Platforms must come from --platform
or environment (.env).

Options:
  --platform <value>  Build only a single platform (e.g., linux/amd64)
  --push              Push images instead of loading locally
  -h, --help      Show this help and exit
USAGE
  exit 1
}

# shellcheck source=../../scripts/common.sh
source "${ROOT_DIR}/scripts/common.sh"

init_supported_lists() {
  split_list "${AICAGE_TOOLS}" TOOLS
  ensure_base_aliases
  split_list "${AICAGE_BASE_ALIASES}" BASES
  [[ ${#TOOLS[@]} -gt 0 ]] || die "AICAGE_TOOLS is empty."
  [[ ${#BASES[@]} -gt 0 ]] || die "AICAGE_BASE_ALIASES is empty."
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
fi

load_env_file
init_supported_lists

platform_override=""
push_flag=""
version_override=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      [[ $# -ge 2 ]] || { echo "[build-all] --platform requires a value" >&2; exit 1; }
      platform_override="$2"
      shift 2
      ;;
    --push)
      push_flag="--push"
      shift
      ;;
    --version)
      [[ $# -ge 2 ]] || { echo "[build-all] --version requires a value" >&2; exit 1; }
      version_override="$2"
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
  echo "[build-all] Building platforms ${platforms[*]}." >&2
else
  die "Platform list is empty; set AICAGE_PLATFORMS or use --platform."
fi

platform_arg=(--platform "${platforms[*]}")
if [[ -n "${version_override}" ]]; then
  AICAGE_VERSION="${version_override}"
fi

for tool in "${TOOLS[@]}"; do
  for base_alias in "${BASES[@]}"; do
    local_platforms="${platforms[*]}"
    echo "[build-all] Building ${tool}-${base_alias} (platforms: ${local_platforms})" >&2
    if [[ -n "${push_flag}" ]]; then
      "${FINAL_DIR}/scripts/build.sh" --tool "${tool}" --base "${base_alias}" "${platform_arg[@]}" "${push_flag}"
    else
      "${FINAL_DIR}/scripts/build.sh" --tool "${tool}" --base "${base_alias}" "${platform_arg[@]}"
    fi
  done
done
