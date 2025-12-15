# aicage CLI task notes

Goal: implement the `aicage` CLI in Python to orchestrate running agent tools in Docker, following
`doc/ai/task/00-aicage-software.md`.

Key behaviors
- CLI syntax: `aicage <docker-run-args?> <tool> <tool-args?>` or `aicage <docker-run-args?> -- <tool> <tool-args?>`.
- Docker args are one opaque string; precedence order for concatenation is CLI > project > global.
- Projects are identified by the resolved absolute cwd when invoked.
- Images live under `wuodan/aicage` with tags `<tool>-<base>-latest`; default base is `ubuntu`.
- Available bases are discovered dynamically from Docker Hub tags (filter `*-latest`), using the same
  logic as `aicage-image`.
- On first run per project+tool, prompt for base (suggest default). If stdin is not a TTY when a
  prompt is needed, abort.
- Always `docker pull` before running. A dry-run prints the final `docker run` command but still
  resolves state.
- Read the `tool_path` label from the image to know which host directory to mount for tool config
  (paths come from the image metadata, e.g., `~/.codex`).

Runtime expectations
- Mount host project realpath to `/workspace` and set workdir `/workspace`.
- Mount the host tool config path to the same path inside the container.
- Include `--rm -it` and pass `AICAGE_UID/GID/USER` so the entrypoint can create a matching user.
- Crash on missing required input in non-interactive contexts; no implicit defaults beyond the
  central config default base.

State layout
- Packaged global config (`config/config.yaml`) defines `image_repository` and `default_image_base`.
- Persistent state lives under `~/.aicage/` with global config (`config.yaml`) and per-project files
  keyed by cwd realpath hash (`projects/<hash>.yaml`). Both support stored docker args and per-tool
  base choices.

Outstanding considerations
- To change stored docker args or base choices after first run, edit the files under `~/.aicage/`.
- Tests are Python `unittest` cases covering parsing, discovery parsing, config persistence, run
  assembly, and non-TTY prompting behavior.
