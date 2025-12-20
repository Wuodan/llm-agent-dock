# Task 05: Lock config file briefly

I want to change the handling of the config file and when the docker image is pulled.

## Config file locking

I want to lock files in `~/.aicage/` to avoid parallel read/writes of several instances of `aicage`.
But the files shall be only locked briefly.

To lock cross-platform, ChatGPT suggested `portalocker`, use that or something else to lock cross-platform without 
tangling with the details.

## Lock briefly

With a bit of restructuring and capsulation we can reduce the time the config files are locked.

Changes to flow: New flow:
1. cli.py calls module `config`
2. module `config` locks the `~/.aicage/config.yaml` and the project file in `~/.aicage/projects/`
3. ask user for anything needed. this includes the question for `base-image` so module `config` calls module `registry` for that but docker pull does not yet happen.
4. module `config` has new config, writes it to config-files if needed
5. module `config` unlocks files, then returns config object (can the config objects easily be made readonly here?)
6. `cli.py` now calls module `registry` to pull image (keeping this separate as I want to do something around this later but not in this session/task)
7. `cli.py` then calls module `runtime` with the config object to get the docker-run args
   The block in `build_run_args()` where the mount preferences are handled and stored must move into the module `config` while files are locked, 
   mount-preferences becomes part of the config object returned by module `config`.
8. `cli.py` uses the docker-run args as it does now to print for dry-run or start a container.

## General coding guidelines

I come from Java and greatly value `Clean Code` and `Separation/Encapsulation`.  
Meaning:
- I want to see datatypes explicitly.
- I want clean capsulation with private/public visibility. Default is always private and visibility is only increased 
  when needed - for files, classes, methods, variables ... everywhere. If this is violated I stop my review immediately
  so get this right.
- pass wrapping objects when you can, don't split wrapping objects into variables
- Respect `doc/python-test-structure-guidelines.md` when it comes to writing tests.

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