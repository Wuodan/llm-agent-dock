#!/usr/bin/env bash

if [[ -z "${AICAGE_BASE_IMAGE:-}" ]]; then
  echo "AICAGE_BASE_IMAGE must be set (use base-images/scripts/test.sh)." >&2
  exit 1
}

require_base_image() {
  if [[ -z "${AICAGE_BASE_IMAGE:-}" ]]; then
    echo "AICAGE_BASE_IMAGE is not configured." >&2
    return 1
  fi
  if ! command -v docker >/dev/null; then
    echo "Docker CLI missing." >&2
    return 1
  fi
}

base_exec() {
  local cmd="$1"
  docker run --rm \
    "${AICAGE_BASE_IMAGE}" \
    /bin/bash -lc "${cmd}"
}
