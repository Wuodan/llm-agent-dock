#!/usr/bin/env bash
set -euo pipefail

TARGET_UID="${AICAGE_UID:-${UID:-1000}}"
TARGET_GID="${AICAGE_GID:-${GID:-1000}}"
TARGET_USER="${AICAGE_USER:-${USER:-aicage}}"

if [[ "${TARGET_UID}" == "0" ]]; then
  exec "$@"
fi

if ! getent group "${TARGET_GID}" >/dev/null; then
  groupadd -g "${TARGET_GID}" "${TARGET_USER}"
fi

if ! getent passwd "${TARGET_UID}" >/dev/null; then
  useradd -m -u "${TARGET_UID}" -g "${TARGET_GID}" -s /bin/bash "${TARGET_USER}"
fi

TARGET_USER="$(getent passwd "${TARGET_UID}" | cut -d: -f1)"
TARGET_HOME="$(getent passwd "${TARGET_UID}" | cut -d: -f6)"
TARGET_HOME="${TARGET_HOME:-/home/${TARGET_USER}}"

mkdir -p /workspace
chown "${TARGET_UID}:${TARGET_GID}" /workspace
chown -R "${TARGET_UID}:${TARGET_GID}" "${TARGET_HOME}"

export HOME="${TARGET_HOME}"
export USER="${TARGET_USER}"
export PATH="${HOME}/.local/bin:${PATH}"

cd /workspace

exec gosu "${TARGET_UID}:${TARGET_GID}" "$@"
