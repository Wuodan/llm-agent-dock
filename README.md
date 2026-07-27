# aicage

Run your favorite AI coding agents comfortably in Docker.

## Why use `aicage`?

Agents need deep access (read code, run shells, install deps).
Their built-in safety checks are naturally limited.

Running agents in containers gives a hard boundary - while the experience stays the same.
See [Why cage agents?](#why-cage-agents) for the full rationale.

## Quick start

Install:

```bash
pipx install aicage
```

In your project directory, run:

```bash
aicage <agent>
```

For a first useful run, you can usually just press Enter or select `OK` when prompted.

- Built-in agent examples:

  ```bash
  aicage agy
  aicage claude
  aicage codex
  aicage copilot
  aicage crush
  aicage droid
  aicage gemini
  aicage goose
  aicage opencode
  aicage qwen
  ```

Your existing CLI config for each agent is mounted inside the container so you can keep using your preferences and
credentials.

## What you see first

After `aicage <agent>` starts, you will see this setup overview:

![Overview screen](https://raw.githubusercontent.com/wiki/aicage/aicage/screenshots/textual/Screenshot_overview.png)

The overview brings the most common choices together in one place:

- `Agent`: the built-in or custom agent you want to run.
- `Bind Mounts`: extra host files and directories the container should be able to access.
- `Base`: the base image used for the agent image. The suggested default is best for most users.
- `Extensions`: optional local additions that install tools or request extra host shares.
- `Docker Args`: extra `docker run` arguments such as `-e`, `-p`, or `--network`.
- `Docker socket`: lets the agent use Docker on the host when you explicitly enable it.
- `Clipboard sharing`: lets agents write to clipboard.
- `OK`: saves the current project config for that agent and starts the container.

## Common next steps

### Bind mounts

Use `Bind Mounts` when the agent needs access to files or directories outside the project.

### Docker args

If you want to adjust how the container starts, open `Docker Args` in the setup screen.

![Docker args](https://raw.githubusercontent.com/wiki/aicage/aicage/screenshots/textual/Screenshot_docker_args.png)

Use it for normal `docker run` arguments such as:

```bash
-e FOO=bar
-p 3000:3000
--network my-net
```

See [Docker run pass-through args](https://github.com/aicage/aicage/wiki/Docker-Args).

### Extensions

Extensions let you add tools on top of an existing agent image. Quick start:

![Extensions](https://raw.githubusercontent.com/wiki/aicage/aicage/screenshots/textual/Screenshot_extensions.png)

```bash
git clone https://github.com/aicage/aicage-custom-samples.git $HOME/.aicage-custom
```

Then rerun `aicage <agent>` and select the extension in the setup screen.
See [Extensions](https://github.com/aicage/aicage/wiki/Customization-Extensions).

### Docker socket access

If you want the agent to run Docker commands, enable `Docker socket` in the setup screen.

### Clipboard sharing

Use `Clipboard sharing` in the setup screen for agents which write to clipboard.

## Full documentation

The complete user documentation lives in the wiki:
[aicage.wiki](https://github.com/aicage/aicage/wiki)

## Common scenarios

- Pass arguments to the agent:
  - `aicage <agent> resume <session-id>`
- Share additional host folders:
  - Use `Shares` or extension-provided shares in the setup UI.
- Use proxies:
  - `aicage` forwards `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY`.
  - See [CLI options](https://github.com/aicage/aicage/wiki/CLI-Options).
- Use host networking or custom networks:
  - See [Host networking](https://github.com/aicage/aicage/wiki/Host-Networking).
- On Windows:
  - set `git config --global core.autocrlf true` on the Windows host to avoid line-ending diffs.
- On macOS with native Docker:
  - See [Known hiccups](https://github.com/aicage/aicage/wiki/Known-Hiccups) for the current support caveat.
- Run into first-use setup issues:
  - See [Known hiccups](https://github.com/aicage/aicage/wiki/Known-Hiccups).
- Add custom tools/agents/base images:
  - [Extensions](https://github.com/aicage/aicage/wiki/Customization-Extensions)
  - [Custom agents](https://github.com/aicage/aicage/wiki/Customization-Agents)
  - [Custom base images](https://github.com/aicage/aicage/wiki/Customization-Base-Images)

## Built-in agents

<!-- pyml disable line-length -->
| CLI      | Agent              | Homepage                                                                                     |
|----------|--------------------|----------------------------------------------------------------------------------------------|
| agy      | Antigravity CLI    | [https://antigravity.google/docs/cli-overview](https://antigravity.google/docs/cli-overview) |
| claude   | Claude Code        | [https://claude.com/product/claude-code](https://claude.com/product/claude-code)             |
| codex    | Codex CLI          | [https://developers.openai.com/codex/cli](https://developers.openai.com/codex/cli)           |
| copilot  | GitHub Copilot CLI | [https://github.com/features/copilot/cli](https://github.com/features/copilot/cli)           |
| crush    | Crush              | [https://github.com/charmbracelet/crush](https://github.com/charmbracelet/crush)             |
| droid    | Factory CLI        | [https://factory.ai/product/cli](https://factory.ai/product/cli)                             |
| gemini   | Gemini CLI         | [https://geminicli.com](https://geminicli.com)                                               |
| goose    | Goose CLI          | [https://goose-docs.ai](https://goose-docs.ai)                                               |
| opencode | OpenCode           | [https://opencode.ai](https://opencode.ai)                                                   |
| qwen     | Qwen Code          | [https://qwenlm.github.io/qwen-code-docs](https://qwenlm.github.io/qwen-code-docs)           |
<!-- pyml enable line-length -->

## Customization

`aicage` lets you customize images at three levels: extensions, agents, and base images. The sample repo is a fast
way to see working examples and copy a template.

Quick start:

```bash
git clone https://github.com/aicage/aicage-custom-samples.git $HOME/.aicage-custom
```

Then run any agent:

```bash
aicage <agent>
```

These are only samples. Use them to learn the structure, then replace or edit them with your own definitions.
`aicage` detects whatever you place under `~/.aicage-custom` and offers it during selection.
Extensions can install tools and request additional host mounts.

After adding or changing custom definitions, restart `aicage`.

- Extensions: [Customization-Extensions](https://github.com/aicage/aicage/wiki/Customization-Extensions)
- Custom agents: [Customization-Agents](https://github.com/aicage/aicage/wiki/Customization-Agents)
- Custom base images: [Customization-Base-Images](https://github.com/aicage/aicage/wiki/Customization-Base-Images)

Image updates are handled automatically; see [Updates](https://github.com/aicage/aicage/wiki/Updates).

## aicage options

- `--dry-run` prints the composed `docker run` command without executing it.
- `--share <path>` mounts a host path into the container at the same path. Repeatable; add `:ro` for read-only.
- Extensions can also request grouped host mounts during setup.

Configuration file formats are documented in [CONFIG.md](CONFIG.md). Extension authoring is documented in
[doc/extensions.md](doc/extensions.md).

## Why cage agents?

AI coding agents read your code, run shells, install packages, and edit files. That power is useful,
but granting it directly on the host expands your risk surface.

Where built-in safety is limited:

- Allow/deny lists only cover known patterns; unexpected commands or attack paths can slip through.
- Some agents work fully only after relaxing their own safety modes, broadening what they can touch.
- “Read-only project” features are software rules. Other projects and files still sit alongside them
  on the same host.

How aicage mitigates this:

- Containers create a practical boundary: the agent can access only what you explicitly mount or share. Day-to-day
  use stays familiar while files you do not mount stay out of reach.
