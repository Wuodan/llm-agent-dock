# 🧠 llm-agent-dock

llm-agent-dock builds ready-to-run Docker images for popular agentic coding assistants. Each image
combines a curated “fat” base OS with a thin layer that installs and configures the selected agent.
The same configuration produces images for `linux/amd64` and `linux/arm64`.

---

## Why Use It?

- **One command, many variants**: Generate every base × tool combination through a single Bake file.
- **Consistent tooling**: Shared packages (git, curl, Python, etc.) plus per-agent installers ensure
  parity across environments.
- **Multi-arch by default**: Buildx and QEMU support mean you can test both architectures locally or
  in CI.
- **Smoke-tested**: Automated Bats suites confirm that containers boot and agent CLIs respond.

---

## Matrix at a Glance

| Base Alias | Image Reference                                |
|------------|------------------------------------------------|
| `act`      | `ghcr.io/catthehacker/ubuntu:act-latest`       |
| `universal`| `ghcr.io/devcontainers/images/universal:2-linux` |
| `ubuntu`   | `ubuntu:24.04`                                 |

| Tool Key          | Description            |
|-------------------|------------------------|
| `cline`           | Cline CLI / VSCode AI  |
| `codex`           | Codex coding agent     |
| `factory_ai_droid`| Factory.AI Droid agent |

Platforms: `linux/amd64`, `linux/arm64`.

---

## Quick Start

> Scripts are introduced gradually; check `git log` or `doc/ai/plan/` for availability while the
> project is under active development.

```bash
# 1) Prepare BuildKit + QEMU emulation
scripts/dev/bootstrap.sh

# 2) Build a specific variant
scripts/build.sh cline ubuntu --platform linux/amd64

# 3) Run smoke tests against a tag
scripts/test.sh ghcr.io/<org>/llm-agent-dock:cline-ubuntu-latest
```

The bootstrap helper also writes a `.env` file with `LLM_AGENT_DOCK_*` defaults so the build/test
scripts share registry, tag, and platform settings. Install `bats` (`brew install bats-core` or
`npm install -g bats`) before running `scripts/test.sh`.

---

## Configuration Defaults

`scripts/dev/bootstrap.sh` seeds a `.env` file in the repo root so every command agrees on image
coordinates:

| Variable | Purpose | Default |
|----------|---------|---------|
| `LLM_AGENT_DOCK_REGISTRY` | Registry hostname used for tags. | `ghcr.io` |
| `LLM_AGENT_DOCK_REPOSITORY` | Namespace/repo appended to the registry. | `wuodan/llm-agent-dock` |
| `LLM_AGENT_DOCK_VERSION` | Tag suffix (format: `<tool>-<base>-<version>`). | `latest` |
| `LLM_AGENT_DOCK_PLATFORMS` | Comma-separated build platforms for Buildx. | `linux/amd64,linux/arm64` |

Override any value via environment variables (`export LLM_AGENT_DOCK_VERSION=dev`) or by editing the
generated `.env`.

---

## Dockerfile Args

The root `Dockerfile` accepts `BASE_IMAGE`, `TOOL`, and `TARGETARCH` build args so every base × tool
variant shares the same definition. You can dry-run it directly while the helper scripts are still
under construction:

```bash
docker build \\
  --build-arg BASE_IMAGE=ubuntu:24.04 \\
  --build-arg TOOL=codex \\
  --build-arg TARGETARCH=amd64 \\
  -t llm-agent-dock:codex-ubuntu .
```

Use `TOOL=cline|codex|factory_ai_droid` and swap `BASE_IMAGE` with any alias from the matrix.

---

## Build Automation

- `docker-bake.hcl` defines one target per base × tool combination plus a `matrix` group so
  `docker buildx bake -f docker-bake.hcl matrix --print` shows the full grid.
- `scripts/build.sh <tool> <base>` wraps Bake with guardrails. Useful flags:
  - `--platform <list>` overrides `LLM_AGENT_DOCK_PLATFORMS`.
  - `--push` / `--load` toggle Buildx outputs.
  - `--print` previews the Bake config for the selected target.
  - `--set key=value` forwards arbitrary Bake overrides (for example, `--set REGISTRY=example.com`).
- All builds tag images as `${LLM_AGENT_DOCK_REGISTRY}/${LLM_AGENT_DOCK_REPOSITORY}:<tool>-<base>-<version>`.

---

## Testing

Smoke tests live under `tests/smoke/` (one Bats suite per tool) and rely on Docker to run each image
under test. Use `scripts/test.sh` to orchestrate them:

```bash
scripts/test.sh ghcr.io/<org>/llm-agent-dock:codex-ubuntu-latest --tool codex --no-pull
```

- `--tool <name>` limits execution to a single suite; omit it to run all suites.
- `--pull` is enabled by default; pass `--no-pull` to use a local image.
- When running Bats manually, export `LLM_AGENT_IMAGE=<tag>` so `tests/smoke/common.bash` knows
  which image to start.

---

## Extending the Catalog

1. **Add a base**:
   - Append the image reference to `docker-bake.hcl` (new target + `matrix` group entry).
   - Adjust the Dockerfile’s base-prep section if the OS needs extra packages.
   - Document the alias in the matrix table.
2. **Add a tool**:
   - Extend the Dockerfile’s installer `case` block and comment where new agents should plug in.
   - Create a Bake target + smoke suite (`tests/smoke/<tool>.bats`).
   - Update scripts/tests to mention the new tool where validation is performed.
3. **Share the process**: Update this README, `AGENTS.md`, and `doc/ai/plan/` so future agents can
   trace decisions and rerun commands.

Need contributor details or current milestones? See `doc/ai/TASK.md` and the latest entries in
`doc/ai/plan/`.

---

## License

Apache-2.0 — see `LICENSE`.
