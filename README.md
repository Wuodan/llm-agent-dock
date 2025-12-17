# aicage

Run your favorite AI coding agents comfortably in Docker.

## Why use `aicage`?

Agents need deep access (read code, run shells, install deps).
Their built-in safety checks are naturally limited.

Running agents in containers gives a hard boundary - while the experience stays the same.
See [Why cage agents?](#why-cage-agents) for the full rationale.

## Quickstart

- Prerequisites:
  - Docker
  - Python 3.10+ and `pipx`
- Install:
  
  ```bash
  pipx install aicage
  ```
  
- Navigate to your project directory.
- Use one of these commands:

  ```bash
  aicage claude
  aicage cline
  aicage codex
  aicage copilot
  aicage droid
  ```

## Base images

The first run asks which base image to use; pick Ubuntu or whatever matches your Linux distro.

| Base   | Distro | Notes                                                                                              |
|--------|--------|----------------------------------------------------------------------------------------------------|
| ubuntu | Ubuntu | Good default for most users                                                                        |
| debian | Debian | For Debian users                                                                                   |
| fedora | Fedora | For RedHat/Fedora users                                                                            |
| alpine | Alpine | Minimal footprint; experimental                                                                    |
| node   | Ubuntu | Official Node image (all base images have Node)                                                    |
| act    | Ubuntu | Default runner image from [act](https://github.com/nektos/act) (`act` runs GitHub Actions locally) |

All base images have the same stack of tools installed.

## Agents

| CLI     | Agent              | Homepage                                                                           |
|---------|--------------------|------------------------------------------------------------------------------------|
| claude  | Claude Code        | [https://claude.com/product/claude-code](https://claude.com/product/claude-code)   |
| cline   | Cline CLI          | [https://docs.cline.bot/cline-cli](https://docs.cline.bot/cline-cli/overview)      |
| codex   | Codex CLI          | [https://developers.openai.com/codex/cli](https://developers.openai.com/codex/cli) |
| copilot | GitHub Copilot CLI | [https://github.com/features/copilot/cli](https://github.com/features/copilot/cli) |
| droid   | Factory CLI        | [https://factory.ai/product/cli](https://factory.ai/product/cli)                   |

Your existing CLI config for each tool is mounted inside the container so you can keep using your
preferences and credentials.

## aicage options

- `--dry-run` prints the composed `docker run` command without executing it.

## Why cage agents?

AI coding agents read your code, run shells, install packages, and edit files. That power is useful,
but granting it directly on the host expands your risk surface.

Where built-in safety is limited:

- Allow/deny lists only cover known patterns; unexpected commands or attack paths can slip through.
- Some tools work fully only after relaxing their own safety modes, broadening what they can touch.
- “Read-only project” features are software rules. Other projects and files still sit alongside them
  on the same host.

How aicage mitigates this:

- Containers create a hard boundary: the agent can access only what you explicitly mount. Day-to-day
  use stays familiar—just with the host kept out of reach.

## Development info

More details are in [DEVELOPMENT.md](DEVELOPMENT.md).
