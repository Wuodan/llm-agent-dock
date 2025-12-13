#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FINAL_DIR="${ROOT_DIR}/final-images"
TOOLS=()
BASES=()

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

# shellcheck source=../../scripts/common.sh
source "${ROOT_DIR}/scripts/common.sh"

init_supported_lists() {
  split_list "${AICAGE_TOOLS}" TOOLS
  ensure_base_aliases
  split_list "${AICAGE_BASE_ALIASES}" BASES
  [[ ${#TOOLS[@]} -gt 0 ]] || die "AICAGE_TOOLS is empty."
  [[ ${#BASES[@]} -gt 0 ]] || die "AICAGE_BASE_ALIASES is empty."
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
    for base_alias in "${BASES[@]}"; do
      local image="${repository}:${tool}-${base_alias}-latest"
      echo "[test-all] Testing ${image}" >&2
      "${FINAL_DIR}/scripts/test.sh" --image "${image}" -- "${BATS_ARGS[@]}"
    done
  done
}

main "$@"
