#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
SUPPORTED_TOOLS=()
SUPPORTED_BASES=()
SUPPORTED_BASE_ALIASES=()

die() {
  echo "[build] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: scripts/build.sh <tool> <base> [options]

Options:
  --platform <value>   Override platform list (default: env or linux/amd64,linux/arm64)
  -h, --help           Show this help and exit

Examples:
  scripts/build.sh cline ubuntu:24.04
  scripts/build.sh codex ghcr.io/catthehacker/ubuntu:act-latest --platform linux/amd64
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

split_list() {
  local raw="$1"
  local -n out=$2
  read -r -a out <<< "${raw}"
}

init_supported_lists() {
  split_list "${AICAGE_TOOLS}" SUPPORTED_TOOLS
  split_list "${AICAGE_BASES}" SUPPORTED_BASES
  split_list "${AICAGE_BASE_ALIASES}" SUPPORTED_BASE_ALIASES
  [[ ${#SUPPORTED_TOOLS[@]} -gt 0 ]] || die "AICAGE_TOOLS is empty; update ${ENV_FILE}."
  [[ ${#SUPPORTED_BASES[@]} -gt 0 ]] || die "AICAGE_BASES is empty; update ${ENV_FILE}."
  [[ ${#SUPPORTED_BASE_ALIASES[@]} -gt 0 ]] || die "AICAGE_BASE_ALIASES is empty; update ${ENV_FILE}."
  [[ ${#SUPPORTED_BASES[@]} -eq ${#SUPPORTED_BASE_ALIASES[@]} ]] || die "AICAGE_BASES and AICAGE_BASE_ALIASES must have the same length."
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    die "Docker CLI not found. Install Docker (with Buildx) first."
  fi
}

slugify_base() {
  local base="$1"
  local slug="${base//\//-}"
  slug="${slug//:/-}"
  echo "${slug}"
}

parse_args() {
  PLATFORM_OVERRIDE=""
  TOOL=""
  BASE=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --platform)
        [[ $# -ge 2 ]] || die "--platform requires a value"
        PLATFORM_OVERRIDE="$2"
        shift 2
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
  init_supported_lists
  require_docker

  contains "${TOOL}" "${SUPPORTED_TOOLS[@]}" || die "Unsupported tool '${TOOL}'. Valid: ${SUPPORTED_TOOLS[*]}"
  contains "${BASE}" "${SUPPORTED_BASES[@]}" || die "Unsupported base '${BASE}'. Valid: ${SUPPORTED_BASES[*]}"

  local repository="${AICAGE_REPOSITORY:-${REPOSITORY:-wuodan/aicage}}"
  local version="${AICAGE_VERSION:-${VERSION:-latest}}"

  local raw_platforms="${PLATFORM_OVERRIDE:-${AICAGE_PLATFORMS:-${PLATFORMS:-}}}"
  [[ -n "${raw_platforms}" ]] || die "Platform list is empty; set AICAGE_PLATFORMS or use --platform."
  local platform_list=()
  split_list "${raw_platforms}" platform_list
  [[ ${#platform_list[@]} -gt 0 ]] || die "Platform list is empty; set AICAGE_PLATFORMS or use --platform."
  local platforms_str="${platform_list[*]}"

  local base_alias=""
  for idx in "${!SUPPORTED_BASES[@]}"; do
    if [[ "${SUPPORTED_BASES[$idx]}" == "${BASE}" ]]; then
      base_alias="${SUPPORTED_BASE_ALIASES[$idx]}"
      break
    fi
  done
  [[ -n "${base_alias}" ]] || die "Base alias not found for '${BASE}'. Check AICAGE_BASES/AICAGE_BASE_ALIASES."

  local target="${TOOL}-${base_alias}"
  local base_image="${BASE}"
  local tag="${repository}:${TOOL}-${base_alias}-${version}"
  local description="Agent image for ${TOOL}"
  local env_prefix=(
    REPOSITORY="${repository}"
    VERSION="${version}"
    PLATFORMS="${platforms_str}"
  )

  local cmd=("env" "${env_prefix[@]}" \
    docker buildx bake \
      -f "${ROOT_DIR}/docker-bake.hcl" \
      agent \
      --set "agent.args.BASE_IMAGE=${base_image}" \
      --set "agent.args.TOOL=${TOOL}" \
      --set "agent.tags=${tag}" \
      --set "agent.labels.org.opencontainers.image.description=${description}" \
      --load
  )

  echo "[build] Target=${target} Platforms=${platforms_str} Repository=${repository} Version=${version} BaseImage=${base_image}" >&2
  "${cmd[@]}"
}

main "$@"
