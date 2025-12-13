#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FINAL_DIR="${ROOT_DIR}/final-images"
SUPPORTED_TOOLS=()
SUPPORTED_BASES=()

die() {
  echo "[build] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: final-images/scripts/build.sh --tool <tool> --base <alias> [options]

Options:
  --tool <value>       Tool name to build (required)
  --base <value>       Base alias to consume (required; must match available base tags)
  --platform <value>   Override platform list (default: env or linux/amd64,linux/arm64)
  --push               Push the image instead of loading it locally
  --version <value>    Override AICAGE_VERSION for this build
  -h, --help           Show this help and exit

Examples:
  final-images/scripts/build.sh --tool cline --base fedora
  final-images/scripts/build.sh --tool codex --base node --platform linux/amd64
USAGE
  exit 1
}

# shellcheck source=../../scripts/common.sh
source "${ROOT_DIR}/scripts/common.sh"

init_supported_lists() {
  split_list "${AICAGE_TOOLS}" SUPPORTED_TOOLS
  ensure_base_aliases
  split_list "${AICAGE_BASE_ALIASES}" SUPPORTED_BASES
  [[ ${#SUPPORTED_TOOLS[@]} -gt 0 ]] || die "AICAGE_TOOLS is empty."
  [[ ${#SUPPORTED_BASES[@]} -gt 0 ]] || die "AICAGE_BASE_ALIASES is empty."
  [[ -n "${AICAGE_BASE_REPOSITORY:-}" ]] || die "AICAGE_BASE_REPOSITORY is empty."
  [[ -n "${AICAGE_VERSION:-}" ]] || die "AICAGE_VERSION is empty."
  if [[ "${AICAGE_BASE_REPOSITORY}" == "${AICAGE_REPOSITORY}" ]]; then
    die "AICAGE_BASE_REPOSITORY must differ from AICAGE_REPOSITORY to keep base images separate."
  fi
}

parse_args() {
  PLATFORM_OVERRIDE=""
  PUSH_MODE="--load"
  VERSION_OVERRIDE=""
  TOOL=""
  BASE_ALIAS=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --tool)
        [[ $# -ge 2 ]] || die "--tool requires a value"
        TOOL="$2"
        shift 2
        ;;
      --base)
        [[ $# -ge 2 ]] || die "--base requires a value"
        BASE_ALIAS="$2"
        shift 2
        ;;
      --platform)
        [[ $# -ge 2 ]] || die "--platform requires a value"
        PLATFORM_OVERRIDE="$2"
        shift 2
        ;;
      --push)
        PUSH_MODE="--push"
        shift
        ;;
      --version)
        [[ $# -ge 2 ]] || die "--version requires a value"
        VERSION_OVERRIDE="$2"
        shift 2
        ;;
      -h|--help)
        usage
        ;;
      --)
        shift
        break
        ;;
      *)
        die "Unknown option '$1'"
        ;;
    esac
  done

  if [[ -z "${TOOL}" || -z "${BASE_ALIAS}" ]]; then
    die "--tool and --base are required"
  fi
}

main() {
  parse_args "$@"
  load_env_file
  if [[ -n "${VERSION_OVERRIDE}" ]]; then
    AICAGE_VERSION="${VERSION_OVERRIDE}"
  fi
  init_supported_lists

  contains "${TOOL}" "${SUPPORTED_TOOLS[@]}" || die "Unsupported tool '${TOOL}'. Valid: ${SUPPORTED_TOOLS[*]}"
  contains "${BASE_ALIAS}" "${SUPPORTED_BASES[@]}" || die "Unsupported base '${BASE_ALIAS}'. Valid: ${SUPPORTED_BASES[*]}"

  local raw_platforms="${PLATFORM_OVERRIDE:-${AICAGE_PLATFORMS:-${PLATFORMS:-}}}"
  [[ -n "${raw_platforms}" ]] || die "Platform list is empty; set AICAGE_PLATFORMS or use --platform."
  local platform_list=()
  split_list "${raw_platforms}" platform_list
  [[ ${#platform_list[@]} -gt 0 ]] || die "Platform list is empty; set AICAGE_PLATFORMS or use --platform."
  local platforms_str="${platform_list[*]}"

  local target="${TOOL}-${BASE_ALIAS}"
  local base_image="${AICAGE_BASE_REPOSITORY}:${BASE_ALIAS}-latest"
  local tag="${AICAGE_REPOSITORY}:${TOOL}-${BASE_ALIAS}-latest"
  local description="Agent image for ${TOOL}"
  local env_prefix=(
    AICAGE_REPOSITORY="${AICAGE_REPOSITORY}"
    AICAGE_VERSION="${AICAGE_VERSION}"
    AICAGE_PLATFORMS="${platforms_str}"
  )

  local cmd=("env" "${env_prefix[@]}" \
    docker buildx bake \
      -f "${FINAL_DIR}/docker-bake.hcl" \
      agent \
      --set "agent.args.BASE_IMAGE=${base_image}" \
      --set "agent.args.TOOL=${TOOL}" \
      --set "agent.tags=${tag}" \
      --set "agent.labels.org.opencontainers.image.description=${description}" \
      "${PUSH_MODE}"
  )

  echo "[build] Target=${target} Platforms=${platforms_str} Repo=${AICAGE_REPOSITORY} Tag=${tag} BaseImage=${base_image} Mode=${PUSH_MODE}" >&2
  "${cmd[@]}"
}

main "$@"
