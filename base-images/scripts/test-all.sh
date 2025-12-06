#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_DIR="${ROOT_DIR}/base-images"
ENV_FILE="${ROOT_DIR}/.env"
BASES=()
BASE_ALIASES=()
BATS_ARGS=()

die() {
  echo "[base-test-all] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: base-images/scripts/test-all.sh [options] [-- <bats-args>]

Runs smoke tests for every base image. Image references are derived from repository/version values.
Bats args after -- are forwarded to each base-images/scripts/test.sh invocation.

Options:
  -h, --help      Show this help and exit

Examples:
  base-images/scripts/test-all.sh
  base-images/scripts/test-all.sh -- --filter base
USAGE
  exit 1
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
  split_list "${AICAGE_BASES}" BASES
  split_list "${AICAGE_BASE_ALIASES}" BASE_ALIASES
  [[ ${#BASES[@]} -gt 0 ]] || die "AICAGE_BASES is empty; update ${ENV_FILE}."
  [[ ${#BASE_ALIASES[@]} -gt 0 ]] || die "AICAGE_BASE_ALIASES is empty; update ${ENV_FILE}."
  [[ ${#BASES[@]} -eq ${#BASE_ALIASES[@]} ]] || die "AICAGE_BASES and AICAGE_BASE_ALIASES must have the same length."
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        ;;
      --)
        shift
        BATS_ARGS=("$@")
        break
        ;;
      *)
        usage
        ;;
    esac
  done
}

main() {
  parse_args "$@"
  load_env_file
  init_supported_lists

  local repository="${AICAGE_BASE_REPOSITORY}"
  local version="${AICAGE_VERSION}"

  for idx in "${!BASES[@]}"; do
    local base_alias="${BASE_ALIASES[$idx]}"
    local image="${repository}:${base_alias}-${version}"
    echo "[base-test-all] Testing ${image}" >&2
    "${BASE_DIR}/scripts/test.sh" --image "${image}" -- "${BATS_ARGS[@]}"
  done
}

main "$@"
