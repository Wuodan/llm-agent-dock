#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SMOKE_DIR="${ROOT_DIR}/tests/smoke"
PULL_IMAGE=1
TOOL_FILTER=""
BATS_ARGS=()
IMAGE_REF=""

usage() {
  cat <<'USAGE'
Usage: scripts/test.sh <image-ref> [options] [-- <bats-args>]

Options:
  --tool <name>   Only run the smoke suite for the specified tool
  --pull          Pull the image before testing (default)
  --no-pull       Skip docker pull (use local image)
  -h, --help      Show this help and exit

Examples:
  scripts/test.sh ghcr.io/example/llm-agent-dock:codex-ubuntu-latest
  scripts/test.sh llm-agent-dock:cline-act-dev --tool cline -- --filter test_cli
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
      --tool)
        [[ $# -ge 2 ]] || usage
        TOOL_FILTER="$2"
        shift 2
        ;;
      --tool=*)
        TOOL_FILTER="${1#*=}"
        shift
        ;;
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
        if [[ -z "${IMAGE_REF}" ]]; then
          IMAGE_REF="$1"
        else
          BATS_ARGS+=("$1")
        fi
        shift
        ;;
    esac
  done

  if [[ -z "${IMAGE_REF}" ]]; then
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
    log "Add tests under tests/smoke or adjust --tool."
    exit 1
  fi

  require_cmd docker
  require_cmd bats

  if (( PULL_IMAGE )); then
    log "Pulling ${IMAGE_REF}"
    if ! docker pull "${IMAGE_REF}"; then
      log "Warning: docker pull failed. Proceeding with local image if available."
    fi
  fi

  log "Running smoke tests via bats"
  LLM_AGENT_IMAGE="${IMAGE_REF}" bats "${bats_path}" "${BATS_ARGS[@]}"
}

parse_args "$@"
run_tests
