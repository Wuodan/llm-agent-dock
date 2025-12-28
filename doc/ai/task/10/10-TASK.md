# Task 10: Naming change "tool" -> "agent"

I originally used the term "tool" in this project but now want to change this to the term "agent" as they are coding agent programms and the term "tool" might be confusing.

So throughout this project find where the term "tool" is used and rename paths, variables, classes, files ... (basically everywhere) to use the new term "agent".

Very important: This project uses docker images produced by the git-submodule `aicage-image` which in uses the bas-images built by `aicage-image-base` (where the entrypoint.sh comes from).

I already updated both submodules (see their last commit).

In this repo, the parts relevant to the entrypoint.sh in docker images have already been updated in last commit but please verify that change.

All other changes to this report for the naming change is still pending. Doinf that is your task.

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