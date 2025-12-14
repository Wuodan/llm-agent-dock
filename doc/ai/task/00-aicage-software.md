# Task: Write `aicage` software

## Introduction

`aicage` is my wrapper to run CLI coding agents (called 'tools` below, examples are: codex, cline, droid, ...) in Docker to separate them from the host OS and disks.

I already have a setup which produces docker images on hub.docker.com, for example `wuodan/aicage:codex-ubuntu-latest`.

Those images all stem from a few base-images (ubuntu, fedora, ...) and have a tool installed in them. In `wuodan/aicage:codex-ubuntu-latest` the base-image is `ubuntu` and the tool is `codex`.

Now I want to write the actual `aicage` software to use those images.

The basic form of usage will be:
1. Navigate to your local project folder
2. Run `aicage codex`

`aicage` shall then do everything needed to start the docker container with all necessary settings.

Examples of such settings:
- mount current host folder as volume
- mount a host folder to persist `tool` settings (`host-tool-settings`)
- optionally additional docker settings (share host VPN, enable docker container to use host docker, etc.)

### Full description of `aicage` run options

`aicage <docker run arguments (optional)> <tool> <tool arguments (optional)>`
or
`aicage <docker run arguments (optional)> -- <tool> <tool arguments (optional)>` with `--` to help parsing


## Details

Here I describe some details of how `aicage` shall function.

### `aicage-folder` on host

Similar to the tools, I want aicage to use a folder `~/.aicage` to persist things.

### Question user what he wants

For some (or all) settings, aicage shall ask the user what he wants.

But we don't want to ask user the same questions on each start. So most questions shall give the users these choices:
- Set forever and don't ask again
- Set for this one run only (possibly store the value and suggest this value next time).

#### Scope of questions

Some questions can have a global scope and some questions are specific to a project (aka host-folder).

Examples of global or project questions:
- Which base-image to use. This might also be project specific in some cases (use-case for later enhancement.)
- Which folder to use for `host-tool-settings` for a given project. Options can be:
  - Use `~/.codex`, the same folder the tool uses when running directly on the host. Thus the credentials and settings are shared.
  - Use a "tool" subfolder of `aicage-folder` on host. Settings are then shared across runs of aicage but not the same as tool on host directly.
  - Use "tool and project" specific subfolder of `aicage-folder` on host. I'm not sure if I want to implement this yet. The tools themselves do not offer this option afaik.
- Storing of <docker run arguments (optional)>: Per project

### <docker run arguments (optional)>

The full form of running `aicage` shall be like
`aicage <docker run arguments (optional)> <tool> <tool arguments (optional)>`
or
`aicage <docker run arguments (optional)> -- <tool> <tool arguments (optional)>`

The `<tool arguments (optional)>` are not persisted.

The idea of the <docker run arguments (optional)> is that a user can place native docker-run arguments. for example when:

- container shall use host VPN (Linux): `--network=host`
- container shall use host gateway: `--add-host=host.docker.internal:host-gateway`

`aicage` shall just store them as string and use them when it executes `docker run`. aicage shall not have a list of possible arguments!

### Installation of aicage

To avoid problems on Windows, `aicage` shall not be written in bash but rather in python or typescript/node.  
With python aicage can easily be installed on the host with `pipx`, with node it can be installed with `npm`.
This choice must be made pretty early and I want you to give me arguments pro/contra either of them, then we discuss and I make that choice.