#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
TOOLS=(cline codex factory_ai_droid)
BASES=(act universal ubuntu)

PULL_IMAGE=1
BATS_ARGS=()

usage() {
  cat <<'USAGE'
Usage: scripts/test-all.sh [options] [-- <bats-args>]

Runs smoke tests for every <tool>-<base> combination. Image references are derived from
registry/repository/version values (defaults align with scripts/build.sh). Options are forwarded to
each scripts/test.sh invocation.

Options:
  --pull          Pull images before testing (default)
  --no-pull       Skip docker pull (use local images)
  -h, --help      Show this help and exit

Examples:
  scripts/test-all.sh --no-pull
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
      --pull)
        PULL_IMAGE=1
        shift
        ;;
      --no-pull)
        PULL_IMAGE=0
        shift
        ;;
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

  local registry="${AICAGE_REGISTRY:-${REGISTRY:-ghcr.io}}"
  local repository="${AICAGE_REPOSITORY:-${REPOSITORY:-wuodan/aicage}}"
  local version="${AICAGE_VERSION:-${VERSION:-latest}}"

  local pull_flag=("--pull")
  if (( PULL_IMAGE == 0 )); then
    pull_flag=("--no-pull")
  fi

  for tool in "${TOOLS[@]}"; do
    for base in "${BASES[@]}"; do
      local image="${registry}/${repository}:${tool}-${base}-${version}"
      echo "[test-all] Testing ${image}" >&2
      "${ROOT_DIR}/scripts/test.sh" "${image}" --tool "${tool}" "${pull_flag[@]}" -- "${BATS_ARGS[@]}"
    done
  done
}

main "$@"
