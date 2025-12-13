#!/usr/bin/env bash
set -euo pipefail

# Package lists live in adjacent text files for easier diffing.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_gosu_from_upstream() {
  local version="${GOSU_VERSION:-1.17}"
  local arch

  case "$(uname -m)" in
    x86_64) arch="amd64" ;;
    aarch64) arch="arm64" ;;
    *)
      echo "Unsupported architecture for gosu: $(uname -m)" >&2
      exit 1
      ;;
  esac

  curl -fsSL \
    "https://github.com/tianon/gosu/releases/download/${version}/gosu-${arch}" \
    -o /usr/local/bin/gosu
  chmod +x /usr/local/bin/gosu
}

generate_locale() {
  if command -v locale-gen >/dev/null 2>&1; then
    locale-gen en_US.UTF-8
  fi
}

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y --no-install-recommends $(cat "${SCRIPT_DIR}/packages-apt.txt")
  rm -rf /var/lib/apt/lists/*
  generate_locale
elif command -v dnf >/dev/null 2>&1; then
  dnf -y makecache
  dnf -y group install development-tools
  dnf -y install $(cat "${SCRIPT_DIR}/packages-dnf.txt")
  dnf clean all
  if ! command -v gosu >/dev/null 2>&1; then
    install_gosu_from_upstream
  fi
else
  echo "Unsupported base image for aicage; apt-get or dnf required" >&2
  exit 1
fi
