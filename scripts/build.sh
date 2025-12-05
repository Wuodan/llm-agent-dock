#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
SUPPORTED_TOOLS=(cline codex factory_ai_droid)
SUPPORTED_BASES=(act universal ubuntu)

die() {
  echo "[build] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: scripts/build.sh <tool> <base> [options]

Options:
  --platform <value>   Override platform list (default: env or linux/amd64,linux/arm64)
  --push               Push images to the registry (sets --push on bake)
  --load               Load images into the local docker image store
  --print              Show bake configuration without building
  --no-cache           Disable build cache
  --set k=v            Forward extra bake --set expressions
  -h, --help           Show this help and exit

Examples:
  scripts/build.sh cline ubuntu
  scripts/build.sh codex act --platform linux/amd64 --push
USAGE
  exit 1
}

contains() {
  local needle=$1; shift
  local item
  for item in "$@"; do
    if [[ "$item" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

load_env_file() {
  if [[ -f "${ENV_FILE}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${ENV_FILE}"
    set +a
  fi
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    die "Docker CLI not found. Install Docker or run scripts/dev/bootstrap.sh first."
  fi
}

parse_args() {
  PLATFORM_OVERRIDE=""
  EXTRA_SET_ARGS=()
  BAKE_FLAGS=()
  TOOL=""
  BASE=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --platform)
        [[ $# -ge 2 ]] || die "--platform requires a value"
        PLATFORM_OVERRIDE="$2"
        shift 2
        ;;
      --platform=*)
        PLATFORM_OVERRIDE="${1#*=}"
        shift
        ;;
      --push|--load|--print|--no-cache)
        BAKE_FLAGS+=("$1")
        shift
        ;;
      --set)
        [[ $# -ge 2 ]] || die "--set requires key=value"
        EXTRA_SET_ARGS+=("$2")
        shift 2
        ;;
      --set=*)
        EXTRA_SET_ARGS+=("${1#*=}")
        shift
        ;;
      -h|--help)
        usage
        ;;
      --)
        shift
        break
        ;;
      *)
        if [[ -z "${TOOL}" ]]; then
          TOOL="$1"
        elif [[ -z "${BASE}" ]]; then
          BASE="$1"
        else
          die "Unexpected argument '$1'"
        fi
        shift
        ;;
    esac
  done

  if [[ -z "${TOOL}" || -z "${BASE}" ]]; then
    usage
  fi
}

main() {
  parse_args "$@"
  load_env_file
  require_docker

  contains "${TOOL}" "${SUPPORTED_TOOLS[@]}" || die "Unsupported tool '${TOOL}'. Valid: ${SUPPORTED_TOOLS[*]}"
  contains "${BASE}" "${SUPPORTED_BASES[@]}" || die "Unsupported base '${BASE}'. Valid: ${SUPPORTED_BASES[*]}"

  local registry="${LLM_AGENT_DOCK_REGISTRY:-${REGISTRY:-ghcr.io}}"
  local repository="${LLM_AGENT_DOCK_REPOSITORY:-${REPOSITORY:-wuodan/llm-agent-dock}}"
  local version="${LLM_AGENT_DOCK_VERSION:-${VERSION:-latest}}"
  local platforms="${PLATFORM_OVERRIDE:-${LLM_AGENT_DOCK_PLATFORMS:-${PLATFORMS:-linux/amd64,linux/arm64}}}"

  local target="${TOOL}-${BASE}"
  local env_prefix=(
    REGISTRY="${registry}"
    REPOSITORY="${repository}"
    VERSION="${version}"
    PLATFORMS="${platforms}"
  )

  local cmd=("env" "${env_prefix[@]}" \
    docker buildx bake \
      -f "${ROOT_DIR}/docker-bake.hcl" \
      "${target}" \
      --set "*.platform=${platforms}"
  )

  if ((${#EXTRA_SET_ARGS[@]})); then
    local set_entry
    for set_entry in "${EXTRA_SET_ARGS[@]}"; do
      [[ -z "${set_entry}" ]] && continue
      cmd+=(--set "${set_entry}")
    done
  fi

  cmd+=("${BAKE_FLAGS[@]}")

  echo "[build] Target=${target} Platforms=${platforms} Registry=${registry}/${repository} Version=${version}" >&2
  "${cmd[@]}"
}

main "$@"
