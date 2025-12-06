#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_DIR="${ROOT_DIR}/base-images"
ENV_FILE="${ROOT_DIR}/.env"
SUPPORTED_BASES=()
SUPPORTED_BASE_ALIASES=()

die() {
  echo "[build-base] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: base-images/scripts/build.sh [--base <ref>] [options]

Options:
  --base <value>       Upstream base image reference (required)
  --platform <value>   Override platform list (default: env or linux/amd64,linux/arm64)
  --push               Push the image instead of loading it locally
  --version <value>    Override AICAGE_VERSION for this build
  -h, --help           Show this help and exit

Examples:
  base-images/scripts/build.sh --base ubuntu:24.04
  base-images/scripts/build.sh --base ghcr.io/catthehacker/ubuntu:act-latest --platform linux/amd64
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
  split_list "${AICAGE_BASES}" SUPPORTED_BASES
  split_list "${AICAGE_BASE_ALIASES}" SUPPORTED_BASE_ALIASES
  [[ ${#SUPPORTED_BASES[@]} -gt 0 ]] || die "AICAGE_BASES is empty; update ${ENV_FILE}."
  [[ ${#SUPPORTED_BASE_ALIASES[@]} -gt 0 ]] || die "AICAGE_BASE_ALIASES is empty; update ${ENV_FILE}."
  [[ ${#SUPPORTED_BASES[@]} -eq ${#SUPPORTED_BASE_ALIASES[@]} ]] || die "AICAGE_BASES and AICAGE_BASE_ALIASES must have the same length."
  [[ -n "${AICAGE_BASE_REPOSITORY:-}" ]] || die "AICAGE_BASE_REPOSITORY is empty; update ${ENV_FILE}."
  [[ -n "${AICAGE_VERSION:-}" ]] || die "AICAGE_VERSION is empty; update ${ENV_FILE}."
  if [[ "${AICAGE_BASE_REPOSITORY}" == "${AICAGE_REPOSITORY}" ]]; then
    die "AICAGE_BASE_REPOSITORY must differ from AICAGE_REPOSITORY to keep base images separate."
  fi
}

parse_args() {
  PLATFORM_OVERRIDE=""
  PUSH_MODE="--load"
  VERSION_OVERRIDE=""
  BASE=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
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

  if [[ -z "${BASE}" ]]; then
    die "--base is required"
  fi
}

main() {
  parse_args "$@"
  load_env_file
  if [[ -n "${VERSION_OVERRIDE}" ]]; then
    AICAGE_VERSION="${VERSION_OVERRIDE}"
  fi
  init_supported_lists

  contains "${BASE}" "${SUPPORTED_BASES[@]}" || die "Unsupported base '${BASE}'. Valid: ${SUPPORTED_BASES[*]}"

  local raw_platforms="${PLATFORM_OVERRIDE:-${AICAGE_PLATFORMS:-${PLATFORMS:-}}}"
  [[ -n "${raw_platforms}" ]] || die "Platform list is empty; set AICAGE_BASE_PLATFORMS or use --platform."
  local platform_list=()
  split_list "${raw_platforms}" platform_list
  [[ ${#platform_list[@]} -gt 0 ]] || die "Platform list is empty; set AICAGE_BASE_PLATFORMS or use --platform."
  local platforms_str="${platform_list[*]}"

  local base_alias=""
  for idx in "${!SUPPORTED_BASES[@]}"; do
    if [[ "${SUPPORTED_BASES[$idx]}" == "${BASE}" ]]; then
      base_alias="${SUPPORTED_BASE_ALIASES[$idx]}"
      break
    fi
  done
  [[ -n "${base_alias}" ]] || die "Base alias not found for '${BASE}'. Check AICAGE_BASES/AICAGE_BASE_ALIASES."

  local target="base-${base_alias}"
  local tag="${AICAGE_BASE_REPOSITORY}:${base_alias}-${AICAGE_VERSION}"
  local description="Base image for aicage (${base_alias})"
  local env_prefix=(
    AICAGE_BASE_REPOSITORY="${AICAGE_BASE_REPOSITORY}"
    AICAGE_VERSION="${AICAGE_VERSION}"
    AICAGE_PLATFORMS="${platforms_str}"
  )

  local cmd=("env" "${env_prefix[@]}" \
    docker buildx bake \
      -f "${BASE_DIR}/docker-bake.hcl" \
      base \
      --set "base.args.BASE_IMAGE=${BASE}" \
      --set "base.tags=${tag}" \
      --set "base.labels.org.opencontainers.image.description=${description}" \
      "${PUSH_MODE}"
  )

  echo "[build-base] Target=${target} Platforms=${platforms_str} Repo=${AICAGE_BASE_REPOSITORY} Version=${AICAGE_VERSION} UpstreamBase=${BASE} Mode=${PUSH_MODE}" >&2
  "${cmd[@]}"
}

main "$@"
