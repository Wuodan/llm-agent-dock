#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_DIR="${ROOT_DIR}/base-images"
SMOKE_DIR="${BASE_DIR}/tests/smoke"
BATS_ARGS=()
IMAGE_REF=""

usage() {
  cat <<'USAGE'
Usage: base-images/scripts/test.sh --image <image-ref> [-- <bats-args>]

Options:
  -h, --help      Show this help and exit

Examples:
  base-images/scripts/test.sh --image wuodan/aicage-base:ubuntu-base-dev
  base-images/scripts/test.sh --image wuodan/aicage-base:act-base-dev -- --filter base
USAGE
  exit 1
}

log() {
  printf '[base-test] %s\n' "$*" >&2
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

run_tests() {
  require_cmd docker
  require_cmd bats

  log "Running base smoke tests via bats"
  AICAGE_BASE_IMAGE="${IMAGE_REF}" bats "${SMOKE_DIR}" "${BATS_ARGS[@]}"
}

parse_args "$@"
run_tests
