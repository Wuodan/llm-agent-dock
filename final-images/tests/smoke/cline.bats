#!/usr/bin/env bats

@test "test_boots_container" {
  run docker run --rm "${AICAGE_IMAGE}" /bin/bash -lc "echo cline-boot && whoami"
  [ "$status" -eq 0 ]
  [[ "$output" == *"cline-boot"* ]]
}

@test "test_runtime_user_creation" {
  run docker run --rm \
    --env AICAGE_UID=1234 \
    --env AICAGE_GID=2345 \
    --env AICAGE_USER=demo \
    "${AICAGE_IMAGE}" \
    /bin/bash -lc "printf '%s\n%s\n%s\n' \"\$(id -u)\" \"\$(id -g)\" \"\${HOME}\""
  [ "$status" -eq 0 ]
  mapfile -t lines <<<"${output}"
  uid="${lines[0]}"
  gid="${lines[1]}"
  home="${lines[2]}"
  [ "${uid}" -eq 1234 ]
  [ "${gid}" -eq 2345 ]
  [[ "${home}" == "/home/demo" ]]
}

@test "test_agent_binary_present" {
  run docker run --rm "${AICAGE_IMAGE}" /bin/bash -lc "command -v cline"
  [ "$status" -eq 0 ]
  [[ "$output" == *"cline"* ]]
}

@test "test_required_packages" {
  run docker run --rm "${AICAGE_IMAGE}" /bin/bash -lc \
    "git --version >/dev/null && python3 --version >/dev/null && node --version >/dev/null && npm --version >/dev/null"
  [ "$status" -eq 0 ]
}
