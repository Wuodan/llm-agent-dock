# Task: Write `aicage` software

## Purpose

`aicage` is a CLI wrapper to run coding agents (called *tools*, e.g. `codex`, `cline`, `droid`) inside Docker containers, isolating them from the host OS while still integrating cleanly with local projects.

Docker images are built and published by the related projects **`aicage-image`** and **`aicage-image-base`** (not by end users).

In normal usage, `aicage` consumes the prebuilt images published under:

* `wuodan/aicage`

Future extensions may allow user-defined images, but this is **out of scope for v1**.

Each image is defined by:

* a **tool** (codex, cline, …)
* a **base image** (ubuntu, fedora, …)

`aicage` is responsible only for **selecting, configuring, and running** these images.

---

## Basic Usage

```bash
cd <project>
aicage codex
```

This starts the appropriate Docker container with:

* current directory mounted as a volume
* persistent tool configuration mounted from the host
* optional user-defined `docker run` arguments

---

## CLI Syntax

```bash
aicage <docker-run-args?> <tool> <tool-args?>
```

or

```bash
aicage <docker-run-args?> -- <tool> <tool-args?>
```

Notes:

* `<docker-run-args>` are passed verbatim to `docker run`
* `<tool-args>` are passed verbatim to the tool inside the container
* `<tool-args>` are **never persisted**
* `--` is supported to disambiguate parsing

---

## Project Definition

A **project** is identified by the **absolute path of the current working directory** when `aicage` is invoked.

No git detection or repo heuristics are used.

---

## Image Selection

Docker images always follow this naming rule:

```
<tool>-<base>-latest
```

Examples:

* `codex-ubuntu-latest`
* `cline-fedora-latest`

### Base Image Selection

* The **tool** is always taken from the CLI argument
* The **base image** is selected per project+tool

A **central default base image** must exist in the code (single variable).

Behavior:

* On first use, the default base is **suggested** to the user
* The user may accept it or choose another available base
* The chosen base is persisted for future runs

#### Available Base Images

Available base images must be determined dynamically.

`aicage` must reuse the same logic already implemented in the **`aicage-image`** project:

* Query Docker Hub API
* Read all tags from the image repository
* Derive valid base images from tags

Instead of `wuodan/aicage-image-base`, the repository to query here is:

* `wuodan/aicage`

This logic must not be re-invented.

---

## Image Pulling

* `aicage` always pulls the image before running it (`docker pull`)
* Future enhancements may add smarter behavior, but **v1 always pulls**

---

## Host Persistence (`~/.aicage`)

`aicage` stores all persistent state under:

```
~/.aicage/
```

This includes:

* global configuration
* per-project configuration
* per-tool configuration

Exact layout is an implementation detail, but **both global and project scopes must be supported in v1**.

---

## Tool Configuration Mounts

Each tool uses a specific configuration directory on the host (e.g. `~/.codex`, `~/.factory`).

Important constraints:

* `aicage` does **not** hardcode tool-specific paths
* Tool configuration paths are provided via **Docker image LABELs**
* `aicage` reads these labels to determine which host directory to mount

This keeps tool knowledge out of `aicage` itself.

---

## Docker Run Arguments

* Docker arguments are treated as **one opaque string**
* `aicage` does not validate, parse, or interpret them
* Arguments may include networking, host access, etc.

Example:

```bash
aicage "--network=host --add-host=host.docker.internal:host-gateway" codex
```

### Persistence and Precedence

Docker arguments may come from multiple sources.

Precedence (highest wins):

1. CLI-provided docker args
2. project-stored docker args
3. global defaults

Arguments are concatenated as strings in that order.

---

## Interactive Questions

Some settings require user decisions (e.g. base image choice).

Rules:

* Questions are asked interactively when possible
* Answers can be stored for future runs
* Users should not be repeatedly asked the same question

### Non-interactive Behavior

If `aicage` requires user input and **stdin is not a TTY**:

* `aicage` must **crash immediately**
* The error message must clearly state which decision is missing
* No defaults or guesses are allowed in v1

---

## Dry Run Mode

`aicage` must support:

```bash
aicage --dry-run ...
```

Behavior:

* Print the fully resolved `docker run` command
* Do not execute it
* Useful for debugging and scripting

---

## Non-Goals (v1)

`aicage` explicitly does **not**:

* manage Docker installation
* validate Docker arguments
* inspect container internals
* contain tool-specific logic beyond reading image labels

---

## Implementation Constraints

* Language: **Python**
* Intended installation method: `pipx`
* Must work on Linux, macOS, and Windows
* Avoid shell-specific behavior

---

## Summary

`aicage` is a thin, predictable orchestration layer:

* no hidden magic
* no implicit defaults
* no Docker semantics

Its job is to reliably turn:

```bash
aicage codex
```

into a correct, debuggable `docker run` invocation.
