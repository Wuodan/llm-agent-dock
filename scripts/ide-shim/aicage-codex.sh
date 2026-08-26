#!/bin/sh

name=${0##*/}
agent=${name#aicage-}
agent=${agent%.sh}

exec /home/stefan/development/github/aicage/aicage/.venv/bin/aicage \
  --stdio \
  --menu none \
  "$agent" "$@"
