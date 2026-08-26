#!/bin/sh

name=${0##*/}
agent=${name#aicage-}
agent=${agent%.sh}

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
log_dir="$script_dir/log"
mkdir -p "$log_dir"
log_file="$log_dir/$agent-$(date +%Y%m%d-%H%M%S).log"

{
  echo "=== aicage-$agent shim ==="
  echo "timestamp: $(date -Iseconds)"
  echo "pwd: $(pwd)"
  echo "agent: $agent"
  printf 'argv: %s\n' "$*"
  echo "argc: $#"
  echo "---"
} >>"$log_file"

# Extra args for sandbox
# Codex uses bubblewrap as sandbox on Linux with '--sandbox' and/or some network settings.
# For simplicity use of bubblewrap is assumed here, which requires docker run args:
# - '--privileged' or
# - '--cap-add SYS_ADMIN --security-opt seccomp=unconfined --security-opt apparmor=unconfined'

exec /home/stefan/development/github/aicage/aicage/.venv/bin/aicage \
  --stdio \
  --menu none \
  --cap-add SYS_ADMIN \
  --security-opt seccomp=unconfined \
  --security-opt apparmor=unconfined \
  -- "$agent" "$@" 2>>"$log_file"
