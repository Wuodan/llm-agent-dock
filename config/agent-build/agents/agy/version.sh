#!/usr/bin/env bash
set -euo pipefail

# Antigravity does not currently publish version metadata through a stable
# public API. Instead, the official install.sh script contains the updater
# base URL which points at platform-specific manifest JSON files.
#
# We deliberately:
#   1. Download the current install.sh from Google.
#   2. Extract AGY_UPDATER_URL from it.
#   3. Query the platform manifest.
#   4. Print the latest version.
#
# This avoids hardcoding Google's current Cloud Run updater URL which may
# change in the future while the install.sh URL remains stable.

INSTALL_URL="https://antigravity.google/cli/install.sh"

# Normalize Linux architecture names to the values used by Antigravity.
arch="$(uname -m)"
case "$arch" in
  x86_64|amd64) arch="amd64" ;;
  aarch64|arm64) arch="arm64" ;;
  *)
    echo "Unsupported architecture: $arch" >&2
    exit 1
    ;;
esac

# Alpine uses musl and requires different binaries.
# Allow manual override for testing.
libc_suffix=""
if [[ "${ANTIGRAVITY_MUSL:-}" == "1" ]] || grep -qi alpine /etc/os-release 2>/dev/null; then
  libc_suffix="_musl"
fi

platform="linux_${arch}${libc_suffix}"
fallback_platform="linux_${arch}"

# Fetch the official installer and discover the current updater endpoint.
install_sh="$(curl -fsSL "$INSTALL_URL")"

base_url="$(
  printf '%s\n' "$install_sh" |
    grep '^DOWNLOAD_BASE_URL=' |
    cut -d'"' -f2
)"

if [[ -z "$base_url" ]]; then
  echo "Failed to extract AGY_UPDATER_URL from ${INSTALL_URL}" >&2
  exit 1
fi

manifest_json="$(curl -fsSL "${base_url}/manifests/${platform}.json" 2>/dev/null || true)"

if [[ -z "$manifest_json" && -n "$libc_suffix" ]]; then
  manifest_json="$(curl -fsSL "${base_url}/manifests/${fallback_platform}.json")"
fi

if [[ -z "$manifest_json" ]]; then
  echo "Failed to fetch manifest for ${platform}" >&2
  exit 1
fi

# Query the platform manifest and print the latest available version.
printf '%s\n' "$manifest_json" | jq -r '.version'
