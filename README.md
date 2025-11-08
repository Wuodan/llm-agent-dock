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

## Extending the Catalog

1. **Add a base**: Register the image alias in `docker-bake.hcl`, tweak the Dockerfile’s base-prep
   section if required, and document it in the matrix table above.
2. **Add a tool**: Implement an installer block inside the Dockerfile, extend the Bake matrix,
   and create `tests/smoke/<tool>.bats`.
3. **Share the process**: Update this README and any relevant plan docs so others can follow along.

Need contributor details or current milestones? See `doc/ai/TASK.md` and the latest entries in
`doc/ai/plan/`.

---

## License

Apache-2.0 — see `LICENSE`.
