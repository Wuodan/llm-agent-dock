#!/usr/bin/env bash
set -euo pipefail

: "${NODEJS_VERSION:?NODEJS_VERSION is required}"
: "${TARGETARCH:?TARGETARCH is required}"

case "${TARGETARCH}" in
  amd64) NODE_DIST_ARCH="x64" ;;
  arm64) NODE_DIST_ARCH="arm64" ;;
  *)
    echo "Unsupported TARGETARCH ${TARGETARCH}" >&2
    exit 1
    ;;
esac

if ! command -v node >/dev/null 2>&1; then
  curl -fsSL "https://nodejs.org/dist/v${NODEJS_VERSION}/node-v${NODEJS_VERSION}-linux-${NODE_DIST_ARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1
fi

ln -sf /usr/local/bin/node /usr/bin/node
ln -sf /usr/local/bin/npm /usr/bin/npm
ln -sf /usr/local/bin/npx /usr/bin/npx

npm config set prefix /usr/local
