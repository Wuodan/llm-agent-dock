#!/usr/bin/env bash

if [[ -z "${LLM_AGENT_IMAGE:-}" ]]; then
  echo "LLM_AGENT_IMAGE must be set (use scripts/test.sh)." >&2
  exit 1
fi

require_llm_agent_image() {
  if [[ -z "${LLM_AGENT_IMAGE:-}" ]]; then
    echo "LLM_AGENT_IMAGE is not configured." >&2
    return 1
  fi
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker CLI missing." >&2
    return 1
  fi
}

agent_exec() {
  local cmd="$1"
  docker run --rm \
    --env LLM_AGENT_IMAGE="${LLM_AGENT_IMAGE}" \
    "${LLM_AGENT_IMAGE}" \
    /bin/bash -lc "${cmd}"
}
