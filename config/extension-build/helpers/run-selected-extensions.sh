#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -eq 0 ]]; then
  exit 0
fi

shopt -s nullglob
mkdir -p /tmp/aicage/scripts-run

for extension in "$@"; do
  scripts_dir="/tmp/aicage/extensions/${extension}/scripts"
  rm -rf /tmp/aicage/scripts-run
  cp -R "${scripts_dir}" /tmp/aicage/scripts-run

  for script in /tmp/aicage/scripts-run/*.sh; do
    echo "Running extension ${extension}: $(basename "${script}")"
    sed -i 's/\r$//' "${script}"
    chmod +x "${script}"
    "${script}"
  done
done

rm -rf /tmp/aicage/scripts-run
