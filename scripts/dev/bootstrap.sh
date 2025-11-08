#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
DEFAULT_BUILDER="${LLM_AGENT_DOCK_BUILDER_NAME:-llm-agent-dock}"
DEFAULT_REGISTRY="${LLM_AGENT_DOCK_REGISTRY:-ghcr.io}"
DEFAULT_REPOSITORY="${LLM_AGENT_DOCK_REPOSITORY:-wuodan/llm-agent-dock}"
DEFAULT_VERSION="${LLM_AGENT_DOCK_VERSION:-dev}"
DEFAULT_PLATFORMS="${LLM_AGENT_DOCK_PLATFORMS:-linux/amd64,linux/arm64}"

log() {
  printf '[bootstrap] %s\n' "$*"
}

ensure_env_file() {
  if [[ -f "${ENV_FILE}" ]]; then
    log "Environment file already exists (${ENV_FILE})."
    return
  fi

  cat >"${ENV_FILE}" <<EOF_ENV
# llm-agent-dock defaults — edit to match your registry/namespace
LLM_AGENT_DOCK_REGISTRY=${DEFAULT_REGISTRY}
LLM_AGENT_DOCK_REPOSITORY=${DEFAULT_REPOSITORY}
LLM_AGENT_DOCK_VERSION=${DEFAULT_VERSION}
LLM_AGENT_DOCK_PLATFORMS=${DEFAULT_PLATFORMS}
EOF_ENV
  log "Wrote default env configuration to ${ENV_FILE}."
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
  ensure_env_file
  ensure_builder
  enable_qemu
  log "Bootstrap complete. Platforms: ${DEFAULT_PLATFORMS}. Override via ${ENV_FILE}."
}

main "$@"
