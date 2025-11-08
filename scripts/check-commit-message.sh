#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/check-commit-message.sh [--message "T123/S045: Summary"] [commit-message-file]

Checks the first line of a commit message for the required prefix format `T###/S###: short summary`.
Options:
  --message <text>   Provide the subject directly instead of reading a file.
  -h, --help         Show this help text.
USAGE
}

subject=""
msg_file=""

while (($#)); do
  case "$1" in
    --message)
      if (($# < 2)); then
        echo "error: --message requires an argument" >&2
        exit 2
      fi
      subject="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "error: unknown option $1" >&2
      usage
      exit 2
      ;;
    *)
      msg_file="$1"
      shift
      ;;
  esac
done

if [[ -z "$subject" ]]; then
  if [[ -n "$msg_file" ]]; then
    if [[ ! -f "$msg_file" ]]; then
      echo "error: commit message file '$msg_file' not found" >&2
      exit 2
    fi
    subject=$(sed -n '1p' "$msg_file")
  else
    echo "error: no commit message supplied" >&2
    usage
    exit 2
  fi
fi

pattern='^T[0-9]{3}/S[0-9]{3}: .+'
if [[ "$subject" =~ $pattern ]]; then
  exit 0
fi

cat >&2 <<EOF
Commit subject must match 'T###/S###: short summary'.
Got: '${subject}'
Examples:
  T004/S001: Define branch workflow policy
  T010/S000: Bootstrap task scaffolding (no subtask)

EOF
exit 1
