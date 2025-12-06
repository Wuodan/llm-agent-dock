#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SMOKE_DIR="${ROOT_DIR}/final-images/tests/smoke"
TOOL_FILTER=""
BATS_ARGS=()
IMAGE_REF=""

usage() {
  cat <<'USAGE'
Usage: final-images/scripts/test.sh --image <image-ref> [options] [-- <bats-args>]

Options:
  --image <ref>   Image reference to test (required)
  --tool <name>   Only run the smoke suite for the specified tool
  -h, --help      Show this help and exit

Examples:
  final-images/scripts/test.sh --image example/aicage:codex-ubuntu-24.04-latest
  final-images/scripts/test.sh --image aicage:cline-ghcr.io-catthehacker-ubuntu-act-latest-dev --tool cline -- --filter test_cli
USAGE
  exit 1
}

log() {
  printf '[test] %s\n' "$*" >&2
}

require_cmd() {
  local bin=$1
  if ! command -v "$bin" >/dev/null 2>&1; then
    log "Missing dependency: $bin"
    if [[ "$bin" == "bats" ]]; then
      log "Install via 'npm install -g bats' or 'brew install bats-core'."
    fi
    exit 1
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --image)
        [[ $# -ge 2 ]] || usage
        IMAGE_REF="$2"
        shift 2
        ;;
      --tool)
        [[ $# -ge 2 ]] || usage
        TOOL_FILTER="$2"
        shift 2
        ;;
      -h|--help)
        usage
        ;;
      --)
        shift
        BATS_ARGS=("$@")
        break
        ;;
      -*)
        usage
        ;;
      *)
        usage
        ;;
    esac
  done

  if [[ -z "${IMAGE_REF}" ]]; then
    log "--image is required"
    usage
  fi
}

select_test_path() {
  if [[ -n "${TOOL_FILTER}" ]]; then
    echo "${SMOKE_DIR}/${TOOL_FILTER}.bats"
  else
    echo "${SMOKE_DIR}"
  fi
}

run_tests() {
  local bats_path
  bats_path="$(select_test_path)"

  if [[ ! -e "${bats_path}" ]]; then
    log "Smoke tests not found at ${bats_path}."
    log "Add tests under final-images/tests/smoke or adjust --tool."
    exit 1
  fi

  require_cmd docker
  require_cmd bats

  log "Running smoke tests via bats"
  AICAGE_IMAGE="${IMAGE_REF}" bats "${bats_path}" "${BATS_ARGS[@]}"
}

parse_args "$@"
run_tests
