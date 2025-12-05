#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
DEFAULT_BUILDER="${AICAGE_BUILDER_NAME:-aicage}"
DEFAULT_REGISTRY="${AICAGE_REGISTRY:-ghcr.io}"
DEFAULT_REPOSITORY="${AICAGE_REPOSITORY:-wuodan/aicage}"
DEFAULT_VERSION="${AICAGE_VERSION:-dev}"
DEFAULT_PLATFORMS="${AICAGE_PLATFORMS:-linux/amd64,linux/arm64}"

log() {
  printf '[bootstrap] %s\n' "$*"
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    log "docker CLI not found; install Docker Desktop or Engine first."
    exit 1
  fi
}

ensure_builder() {
  require_docker
  if docker buildx inspect "${DEFAULT_BUILDER}" >/dev/null 2>&1; then
    log "Using existing buildx builder '${DEFAULT_BUILDER}'."
    docker buildx use "${DEFAULT_BUILDER}"
    return
  fi

  log "Creating buildx builder '${DEFAULT_BUILDER}'."
  docker buildx create --name "${DEFAULT_BUILDER}" --driver docker-container --use
}

enable_qemu() {
  log "Ensuring binfmt emulation for multi-arch builds."
  if docker run --privileged --rm tonistiigi/binfmt --install arm64,amd64 >/dev/null 2>&1; then
    log "binfmt handlers installed."
  else
    log "Warning: failed to configure binfmt (requires privileged Docker)."
    log "Multi-arch builds may be limited until binfmt is installed manually."
  fi
}

main() {
  ensure_builder
  enable_qemu
  log "Bootstrap complete. Platforms: ${DEFAULT_PLATFORMS}. Override via ${ENV_FILE}."
}

main "$@"
