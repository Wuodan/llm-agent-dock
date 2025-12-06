#!/usr/bin/env bats

load './common.bash'

setup_file() {
  require_base_image
}

@test "base image has core runtimes" {
  run base_exec "node --version >/dev/null && python3 --version >/dev/null"
  [ "$status" -eq 0 ]
}

@test "base image has tooling" {
  run base_exec "pipx --version >/dev/null && git --version >/dev/null && ripgrep --version >/dev/null"
  [ "$status" -eq 0 ]
}
