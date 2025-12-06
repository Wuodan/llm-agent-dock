#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
SUPPORTED_TOOLS=(cline codex droid)
SUPPORTED_BASES=(act ubuntu)

die() {
  echo "[build] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: scripts/build.sh <tool> <base> [options]

Options:
  --platform <value>   Override platform list (default: env or linux/amd64,linux/arm64)
  --load               Load images into the local docker image store
  --print              Show bake configuration without building
  --no-cache           Disable build cache
  -h, --help           Show this help and exit

Examples:
  scripts/build.sh cline ubuntu
  scripts/build.sh codex act --platform linux/amd64 --load
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
    die "Docker CLI not found. Install Docker (with Buildx) first."
  fi
}

parse_args() {
  PLATFORM_OVERRIDE=""
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
      --load|--print|--no-cache)
        BAKE_FLAGS+=("$1")
        shift
        ;;
      -h|--help)
        usage
        ;;
      --)
        shift
        break
        ;;
      -*)
        die "Unknown option '$1'"
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

  local repository="${AICAGE_REPOSITORY:-${REPOSITORY:-wuodan/aicage}}"
  local version="${AICAGE_VERSION:-${VERSION:-latest}}"
  local platforms="${PLATFORM_OVERRIDE:-${AICAGE_PLATFORMS:-${PLATFORMS:-linux/amd64,linux/arm64}}}"

  local target="${TOOL}-${BASE}"
  local env_prefix=(
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

  cmd+=("${BAKE_FLAGS[@]}")

  echo "[build] Target=${target} Platforms=${platforms} Repository=${repository} Version=${version}" >&2
  "${cmd[@]}"
}

main "$@"
