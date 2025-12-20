# Task 06: Add command arguments to `aicage`

Calling `aicage` currently has a parameter `--dry-run` which prints the docker command instead of running the command.

I want you to add more such parameters.

## --entrypoint <path>

Example:
`aicage --entrypoint.sh ../some-file.sh codex`

- `--entrypoint` followed by a path. This path must be mounted to `/usr/local/bin/entrypoint.sh` in the container thus overriding the normal entrypoint script.
`codex` is the agent to run (implemented, don't bother).

Check if the path to the file on host exists as file, and is executable (for Linux, unsure how to handle on Windows)
Exit with error message if not.

When this is used, ask the user if it shall be persisted in the project-config.  
If it's in the project config from an earlier run then use it without asking.


## --docker

The `--docker` param is a shorthand for adding the docker.sock to the image as in:
`aicage -v /run/docker.sock:/run/docker.sock <agent`

This should also be persisted in the project config file with a question (same as --entrypoint)

## --config print

`--config list` prints:
- the path to the yaml project-config file in `~/.aicage/project`.
- the content of that file
Add some text to keep those two parts apart.

The full command for this would be `aicage --config print` and no agent after it.

Keep this modular, I might add other sub-params like `print` to `--config`

## Summary of changes

Don't forget the existing arguments before the agent (arguments to docker-run 
`aicage -v /run/docker.sock:/run/docker.sock -- <agent>` already works now) and that anything after the agent has to 
be appended to the CMD (as of now).

Full call examples with `codex` as example agent:
```bash
# basic
aicage codex
# config print
aicage --config print
# full with all optionals parameters in []
aicage [--docker] [--entrypoint path-to-entrypoint] [other arguments for docker-run] AGENT [arguments for agent]
```

## Coding, testing, debugging

Read AGENTS.md and use the existing venv in `.venv`. As always I expect clean-code, like to see datatypes declared 
explicitly, and expect visibility to be minimal (prefixed with _ whatever you can, files, methods, classes, variables) 
in changed or added code.

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
