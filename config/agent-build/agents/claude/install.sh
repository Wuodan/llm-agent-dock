#!/usr/bin/env bash
set -euo pipefail

# Workaround for Claude 2.1.242/2.1.243 with glibc 2.44 on Arch Linux
# Claude 2.1.242/2.1.243 exports allocator symbols and crashes during glibc 2.44
# locale startup on Arch.
if command -v pacman >/dev/null 2>&1; then
  claude_version="$(curl -fsSL https://downloads.claude.ai/claude-code-releases/latest)"
  glibc_version="$(pacman -Q glibc | awk '{print $2}')"
  if [[ "${glibc_version}" == 2.44* && "${claude_version}" =~ ^2\.1\.(242|243)$ ]]; then
    glibc_package="$(mktemp)"
    glibc_locales_package="$(mktemp)"
    curl -fsSL \
      https://archive.archlinux.org/packages/g/glibc/glibc-2.43%2Br37%2Bgfdf10644d6ee-1-x86_64.pkg.tar.zst \
      -o "${glibc_package}"
    curl -fsSL \
      https://archive.archlinux.org/packages/g/glibc-locales/glibc-locales-2.43%2Br37%2Bgfdf10644d6ee-1-x86_64.pkg.tar.zst \
      -o "${glibc_locales_package}"
    {
      echo "213332b0d5b712c20a12dd61d96ba4c21f192df63d454a94ad5cef2b7864e8d1  ${glibc_package}"
      echo "a61640f79ac13ff978ed047ddbf91be8cb12cfbeaeff587aeb6d89e4b5201165  ${glibc_locales_package}"
    } |
      sha256sum -c -
    pacman -U --noconfirm "${glibc_package}" "${glibc_locales_package}"
  fi
fi

# Install Claude using the official installer.
curl -fsSL https://claude.ai/install.sh | bash

# Ensure the binary is on the global PATH for the runtime user.
if [[ -x "/root/.local/bin/claude" ]]; then
  install -m 0755 /root/.local/bin/claude /usr/local/bin/claude
elif command -v claude >/dev/null 2>&1; then
  # Fallback: copy whatever the installer placed on PATH.
  install -m 0755 "$(command -v claude)" /usr/local/bin/claude
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "[install_claude] 'claude' executable not found after installation." >&2
  exit 1
fi
