#!/usr/bin/env bats

@test "base image has core runtimes" {
  run docker run --rm "${AICAGE_BASE_IMAGE}" /bin/bash -lc "echo base-smoke"
  [ "$status" -eq 0 ]
  [[ "$output" == *"base-smoke"* ]]
}
