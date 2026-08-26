#!/bin/sh

name=${0##*/}
agent=${name#aicage-}
agent=${agent%.sh}

exec aicage --stdio --menu none "$agent" "$@"
