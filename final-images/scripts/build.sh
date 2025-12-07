#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FINAL_DIR="${ROOT_DIR}/final-images"
BASE_DIR="${ROOT_DIR}/base-images"
SUPPORTED_TOOLS=()
SUPPORTED_BASES=()
SUPPORTED_BASE_ALIASES=()

die() {
  echo "[build] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: final-images/scripts/build.sh --tool <tool> --base <base> [options]

Options:
  --tool <value>       Tool name to build (required)
  --base <value>       Base alias to consume (required; must match AICAGE_BASES entry)
  --platform <value>   Override platform list (default: env or linux/amd64,linux/arm64)
  --push               Push the image instead of loading it locally
  --version <value>    Override AICAGE_VERSION for this build
  -h, --help           Show this help and exit

Examples:
  final-images/scripts/build.sh --tool cline --base ubuntu:24.04
  final-images/scripts/build.sh --tool codex --base ghcr.io/catthehacker/ubuntu:act-latest --platform linux/amd64
USAGE
  exit 1
}

# shellcheck source=../../scripts/common.sh
source "${ROOT_DIR}/scripts/common.sh"

init_supported_lists() {
  split_list "${AICAGE_TOOLS}" SUPPORTED_TOOLS
  split_list "${AICAGE_BASES}" SUPPORTED_BASES
  split_list "${AICAGE_BASE_ALIASES}" SUPPORTED_BASE_ALIASES
  [[ ${#SUPPORTED_TOOLS[@]} -gt 0 ]] || die "AICAGE_TOOLS is empty."
  [[ ${#SUPPORTED_BASES[@]} -gt 0 ]] || die "AICAGE_BASES is empty."
  [[ ${#SUPPORTED_BASE_ALIASES[@]} -gt 0 ]] || die "AICAGE_BASE_ALIASES is empty."
  [[ ${#SUPPORTED_BASES[@]} -eq ${#SUPPORTED_BASE_ALIASES[@]} ]] || die "AICAGE_BASES and AICAGE_BASE_ALIASES must have the same length."
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
  BASE=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --tool)
        [[ $# -ge 2 ]] || die "--tool requires a value"
        TOOL="$2"
        shift 2
        ;;
      --base)
        [[ $# -ge 2 ]] || die "--base requires a value"
        BASE="$2"
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

  if [[ -z "${TOOL}" || -z "${BASE}" ]]; then
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
  contains "${BASE}" "${SUPPORTED_BASES[@]}" || die "Unsupported base '${BASE}'. Valid: ${SUPPORTED_BASES[*]}"

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
  local base_image="${AICAGE_BASE_REPOSITORY}:${base_alias}-${AICAGE_VERSION}"
  local tag="${AICAGE_REPOSITORY}:${TOOL}-${base_alias}-${AICAGE_VERSION}"
  local description="Agent image for ${TOOL}"
  local env_prefix=(
    AICAGE_REPOSITORY="${AICAGE_REPOSITORY}"
    AICAGE_VERSION="${AICAGE_VERSION}"
    AICAGE_PLATFORMS="${platforms_str}"
  )

  local cmd=("env" "${env_prefix[@]}" \
    docker buildx bake \
      -f "${BASE_DIR}/docker-bake.hcl" \
      -f "${FINAL_DIR}/docker-bake.hcl" \
      base \
      agent \
      --set "base.args.BASE_IMAGE=${BASE}" \
      --set "base.tags=${base_image}" \
      --set "agent.contexts.base=target:base" \
      --set "agent.args.BASE_IMAGE=base" \
      --set "agent.args.TOOL=${TOOL}" \
      --set "agent.tags=${tag}" \
      --set "agent.labels.org.opencontainers.image.description=${description}" \
      "${PUSH_MODE}"
  )

  echo "[build] Target=${target} Platforms=${platforms_str} Repo=${AICAGE_REPOSITORY} Version=${AICAGE_VERSION} BaseImage=${base_image} Mode=${PUSH_MODE} (building base+agent together)" >&2
  "${cmd[@]}"
}

main "$@"
