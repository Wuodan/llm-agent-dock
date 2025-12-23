# Task 07: Use same folder-path as on host

This project `aicage` currently mounts the hosts current folder to /workspace in docker containers.

And `scripts/entrypoint.sh` in the submodule `aicage-image-base` also uses `/workspace`.

I want to extend this by:
1) submodule `aicage-image-base`:
   - Adding an ENV var AICAGE_WORKSPACE to the image in `Dockerfile`, default /workspace
   - Change `scripts/entrypoint.sh` so it uses that ENV var. if AICAGE_WORKSPACE is not defined, it sets it to 
     /workspace early on.
   - Update `bats` tests in submodule `aicage-image-base` to test this. It's time to split the entrypoint tests as the 
     file is becoming large. These are the test-files for entrypoint:
     - tests/smoke/default/90-entrypoint.bats
     - tests/smoke/minimal/90-entrypoint.bats
2) this repo `aicage`
   - keeps mounting current folder to /workspace
   - additionally mounts current folder to the same path as on host in the image
   - sets ENV var AICAGE_WORKSPACE to current folder when it call docker-run

## Task Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:
1. Read documentation and code to understand the task. 
2. Aks me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml`
6. Present me the change for review
7. Interactively react to my review feedback