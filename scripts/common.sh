#!/usr/bin/env bash
set -euo pipefail

_die() {
  if command -v die >/dev/null 2>&1; then
    die "$@"
  else
    echo "[common] $*" >&2
    exit 1
  fi
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
  local env_file="${ROOT_DIR}/.env"

  # The read condition handles files that omit a trailing newline.
  while IFS= read -r line || [[ -n "${line}" ]]; do
    [[ -z "${line}" || "${line}" =~ ^[[:space:]]*# ]] && continue
    if [[ "${line}" =~ ^([^=]+)=(.*)$ ]]; then
      local key="${BASH_REMATCH[1]}"
      local value="${BASH_REMATCH[2]}"
      if [[ -z ${!key+x} ]]; then
        if [[ "${value}" =~ ^\".*\"$ ]]; then
          value="${value:1:${#value}-2}"
        fi
        export "${key}=${value}"
      fi
    fi
  done < "${env_file}"
}

split_list() {
  local raw="$1"
  local -n out=$2
  read -r -a out <<< "${raw}"
}

discover_base_aliases() {
  local repo="${AICAGE_BASE_REPOSITORY:-}"
  [[ -n "${repo}" ]] || _die "AICAGE_BASE_REPOSITORY is empty; set it in .env."

  local -a aliases=()
  if command -v docker >/dev/null 2>&1; then
    while IFS=' ' read -r image_repo image_tag; do
      [[ "${image_repo}" == "${repo}" && "${image_tag}" == *-latest ]] || continue
      aliases+=("${image_tag%-latest}")
    done < <(docker images --format '{{.Repository}} {{.Tag}}' "${repo}" 2>/dev/null || true)
  fi

  if [[ ${#aliases[@]} -eq 0 ]]; then
    local hub_repo="${repo#docker.io/}"
    if [[ "${hub_repo}" == */* && "${hub_repo}" != *.*/* ]]; then
      if command -v curl >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
        mapfile -t aliases < <(python3 - "${hub_repo}" <<'PY'
import json
import sys
import urllib.request

repo = sys.argv[1]
url = f"https://registry.hub.docker.com/v2/repositories/{repo}/tags?page_size=100"
aliases = set()

while url:
    with urllib.request.urlopen(url) as resp:  # noqa: S310 (trusted URL)
        data = json.load(resp)
    for name in (item.get("name", "") for item in data.get("results", [])):
        if name.endswith("-latest"):
            aliases.add(name[:-7])
    url = data.get("next")

for alias in sorted(aliases):
    print(alias)
PY
)
      else
        _die "curl and python3 are required to discover base aliases for ${repo}."
      fi
    else
      _die "Automatic base alias discovery supports Docker Hub repos (namespace/name). Set AICAGE_BASE_ALIASES manually."
    fi
  fi

  [[ ${#aliases[@]} -gt 0 ]] || _die "No base aliases discovered for ${repo}; set AICAGE_BASE_ALIASES explicitly."
  printf '%s\n' "${aliases[*]}"
}

ensure_base_aliases() {
  if [[ -z "${AICAGE_BASE_ALIASES:-}" ]]; then
    AICAGE_BASE_ALIASES="$(discover_base_aliases)"
  fi
}
