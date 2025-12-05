#!/usr/bin/env bats

load './common.bash'

setup_file() {
  require_aicage_image
}

@test "test_boots_container" {
  run agent_exec "echo factory-boot && ls /usr/local/bin | head -n 1"
  [ "$status" -eq 0 ]
  [[ "$output" == *"factory-boot"* ]]
}

@test "test_runtime_user_creation" {
  run agent_exec "printf '%s\n%s\n%s\n' \"\$(id -u)\" \"\$(id -g)\" \"\${HOME}\"" \
    --env AICAGE_UID=1234 \
    --env AICAGE_GID=2345 \
    --env AICAGE_USER=demo
  [ "$status" -eq 0 ]
  IFS=$'\n' read -r uid gid home <<<"${output}"
  [ "${uid}" -eq 1234 ]
  [ "${gid}" -eq 2345 ]
  [[ "${home}" == "/home/demo" ]]
}

@test "test_agent_binary_present" {
  run agent_exec "command -v factory_ai_droid"
  [ "$status" -eq 0 ]
  [[ "$output" == *"factory_ai_droid"* ]]
}

@test "test_required_packages" {
  run agent_exec "git --version >/dev/null && python3 --version >/dev/null && node --version >/dev/null && npm --version >/dev/null"
  [ "$status" -eq 0 ]
}
