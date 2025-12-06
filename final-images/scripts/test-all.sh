#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FINAL_DIR="${ROOT_DIR}/final-images"
ENV_FILE="${ROOT_DIR}/.env"
TOOLS=()
BASES=()
BASE_ALIASES=()

BATS_ARGS=()

die() {
  echo "[test-all] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: final-images/scripts/test-all.sh [options] [-- <bats-args>]

Runs smoke tests for every <tool>-<base> combination. Image references are derived from
repository/version values (defaults align with final-images/scripts/build.sh). Bats args after -- are
forwarded to each final-images/scripts/test.sh invocation.

Options:
  -h, --help      Show this help and exit

Examples:
  final-images/scripts/test-all.sh
  final-images/scripts/test-all.sh -- --filter test_runtime_user_creation
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
  split_list "${AICAGE_TOOLS}" TOOLS
  split_list "${AICAGE_BASES}" BASES
  split_list "${AICAGE_BASE_ALIASES}" BASE_ALIASES
  [[ ${#TOOLS[@]} -gt 0 ]] || die "AICAGE_TOOLS is empty; update ${ENV_FILE}."
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

  local repository="${AICAGE_REPOSITORY}"
  local version="${AICAGE_VERSION}"

  for tool in "${TOOLS[@]}"; do
    for idx in "${!BASES[@]}"; do
      local base="${BASES[$idx]}"
      local base_alias="${BASE_ALIASES[$idx]}"
      local image="${repository}:${tool}-${base_alias}-${version}"
      echo "[test-all] Testing ${image}" >&2
      "${FINAL_DIR}/scripts/test.sh" "${image}" --tool "${tool}" -- "${BATS_ARGS[@]}"
    done
  done
}

main "$@"
