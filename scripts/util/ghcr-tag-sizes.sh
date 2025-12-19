#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./ghcr-tag-sizes.sh <owner> <image>
# Example:
#   ./ghcr-tag-sizes.sh aicage aicage
#
# Outputs:
#   tag<TAB>arch<TAB>size_mb
# For single-arch tags, arch will be "single".
# For multi-arch tags, one line per arch plus a "TOTAL" line per tag.

OWNER="${1:-}"
IMAGE="${2:-}"
if [[ -z "${OWNER}" || -z "${IMAGE}" ]]; then
  echo "Usage: $0 <owner> <image>" >&2
  exit 2
fi

REPO="ghcr.io/${OWNER}/${IMAGE}"

sum_manifest_layers_bytes() {
  # $1 = reference (docker://... or docker://...@sha256:...)
  local ref="$1"
  skopeo inspect --raw "${ref}" \
    | jq -r '([.layers[]?.size] | add) // 0'
}

inspect_tag_sizes() {
  # $1 = tag name
  local tag="$1"
  local ref="docker://${REPO}:${tag}"

  # Determine whether this is a manifest list/index (multi-arch) or a single manifest.
  if skopeo inspect --raw "${ref}" | jq -e '.manifests? != null' >/dev/null 2>&1; then
    # Multi-arch: iterate per-platform digest
    local total=0
    skopeo inspect --raw "${ref}" \
      | jq -r '.manifests[] | [.digest, (.platform.architecture // "unknown"), (.platform.os // "unknown")] | @tsv' \
      | while IFS=$'\t' read -r digest arch os; do
          # Sum sizes for the per-arch manifest (note: per-arch size is compressed sum of layer sizes)
          bytes="$(sum_manifest_layers_bytes "docker://${REPO}@${digest}")"
          total=$(( total + bytes ))
          mb="$(awk -v b="${bytes}" 'BEGIN{printf "%.2f", b/1024/1024}')"
          printf "%s\t%s/%s\t%s\n" "${tag}" "${os}" "${arch}" "${mb}"
        done

    # The "total" of per-arch manifests is not a registry-defined concept, but it's useful for comparison.
    # We compute it as the sum of the per-arch compressed sizes we just printed.
    # To avoid bash subshell scoping issues, recompute total with jq in one go:
    total_bytes="$(
      skopeo inspect --raw "${ref}" \
        | jq -r '.manifests[].digest' \
        | while read -r d; do sum_manifest_layers_bytes "docker://${REPO}@${d}"; done \
        | awk '{s+=$1} END{print s+0}'
    )"
    total_mb="$(awk -v b="${total_bytes}" 'BEGIN{printf "%.2f", b/1024/1024}')"
    printf "%s\tTOTAL\t%s\n" "${tag}" "${total_mb}"
  else
    # Single-arch manifest
    bytes="$(sum_manifest_layers_bytes "${ref}")"
    mb="$(awk -v b="${bytes}" 'BEGIN{printf "%.2f", b/1024/1024}')"
    printf "%s\tsingle\t%s\n" "${tag}" "${mb}"
  fi
}

# List tags and inspect each.
skopeo list-tags "docker://${REPO}" \
  | jq -r '.Tags[]' \
  | while read -r tag; do
      inspect_tag_sizes "${tag}"
    done
