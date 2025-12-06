#!/usr/bin/env bash

if [[ -z "${AICAGE_IMAGE:-}" ]]; then
  echo "AICAGE_IMAGE must be set (use final-images/scripts/test.sh)." >&2
  exit 1
fi

require_aicage_image() {
  if [[ -z "${AICAGE_IMAGE:-}" ]]; then
    echo "AICAGE_IMAGE is not configured." >&2
    return 1
  fi
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker CLI missing." >&2
    return 1
  fi
}

agent_exec() {
  local cmd="$1"
  shift || true
  docker run --rm \
    --env AICAGE_IMAGE="${AICAGE_IMAGE}" \
    "$@" \
    "${AICAGE_IMAGE}" \
    /bin/bash -lc "${cmd}"
}
