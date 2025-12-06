#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
TOOLS=(cline codex droid)
BASES=(act ubuntu)

BATS_ARGS=()

usage() {
  cat <<'USAGE'
Usage: scripts/test-all.sh [options] [-- <bats-args>]

Runs smoke tests for every <tool>-<base> combination. Image references are derived from
repository/version values (defaults align with scripts/build.sh). Bats args after -- are forwarded to
each scripts/test.sh invocation.

Options:
  -h, --help      Show this help and exit

Examples:
  scripts/test-all.sh
  scripts/test-all.sh -- --filter test_runtime_user_creation
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

  local repository="${AICAGE_REPOSITORY:-${REPOSITORY:-wuodan/aicage}}"
  local version="${AICAGE_VERSION:-${VERSION:-latest}}"

  for tool in "${TOOLS[@]}"; do
    for base in "${BASES[@]}"; do
      local image="${repository}:${tool}-${base}-${version}"
      echo "[test-all] Testing ${image}" >&2
      "${ROOT_DIR}/scripts/test.sh" "${image}" --tool "${tool}" -- "${BATS_ARGS[@]}"
    done
  done
}

main "$@"
