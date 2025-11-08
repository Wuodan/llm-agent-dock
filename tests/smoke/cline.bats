#!/usr/bin/env bats

load './common.bash'

setup_file() {
  require_llm_agent_image
}

@test "test_boots_container" {
  run agent_exec "echo cline-boot && whoami"
  [ "$status" -eq 0 ]
  [[ "$output" == *"cline-boot"* ]]
}

@test "test_agent_binary_present" {
  run agent_exec "command -v cline"
  [ "$status" -eq 0 ]
  [[ "$output" == *"cline"* ]]
}

@test "test_required_packages" {
  run agent_exec "git --version >/dev/null && python3 --version >/dev/null && node --version >/dev/null && npm --version >/dev/null"
  [ "$status" -eq 0 ]
}
