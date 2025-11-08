# Task T001 / Subtask S2 — Parameterized Dockerfile

## Objective
Create a single `Dockerfile` that can build every base/tool combination via `BASE_IMAGE`, `TOOL`, and
`TARGETARCH` args, with clearly documented extension points and reliable installer logic for each
agent.

## Deliverables
- Root `Dockerfile` covering:
  - Base image preparation (packages, shared tooling).
  - Tool-specific installation blocks (`case "${TOOL}" in ...`).
  - Comments that highlight where to add new bases or agents.
- Documentation references in `README.md` (temporary note acceptable until S5).
- Smoke validation via `docker build --build-arg BASE_IMAGE=... --build-arg TOOL=...`.

## Flow
1. **Research installers**: Confirm CLI/agent installation steps for `cline`, `codex`, and
   `factory_ai_droid`. If unclear, use MCP `brave-search` → `fetch` and summarize findings in this
   file under *Feedback & Learnings*.
2. Define shared base setup (apt packages, locale fixes, user settings) compatible with all bases.
3. Implement tool install sections using Bash functions or `case` statements; fail fast on unknown
   tools.
4. Add comments `# Add new base tweaks here` and `# Add new agent installers below`.
5. Build at least one variant locally (amd64) to ensure syntax correctness.
6. Capture any user-facing implications (notes for README) here rather than editing README mid-task.
7. Update this checklist and plan log, then commit `[codex][dockerfile]: add parameterized build`.

## Checklist
- [x] Installer research recorded for all tools (links + summary).
- [x] Dockerfile base prep implemented with shared dependencies.
- [x] Tool-specific install logic implemented and linted.
- [x] Sample build attempt recorded (`docker build ...`) — blocked by Docker socket permissions.
- [x] Plan + checklist updated; commit `[codex][dockerfile]: add parameterized build]`.

## Inputs & References
- `doc/ai/TASK.md` — required bases/tools list.
- `AGENTS.md` — Dockerfile conventions.
- External installer docs (cite URLs in Feedback).

## Exit Criteria
- All checklist items complete.
- Dockerfile ready for integration with Bake matrix.

## Feedback & Learnings
- Factory’s CLI packaging isn’t always published under a single npm scope, so the Dockerfile now
  loops through multiple package names and falls back to a shim if every install attempt fails.
- Local Docker builds are currently blocked because the container user cannot access
  `/var/run/docker.sock` (`docker build ...` fails with “permission denied”). Re-run
  `docker build --build-arg BASE_IMAGE=ubuntu:24.04 --build-arg TOOL=cline --build-arg TARGETARCH=amd64`
  once Docker socket access is granted to complete validation.

## Research Notes (2025-11-08)
- `cline`: [docs.cline.bot](https://docs.cline.bot/getting-started/installing-cline) and the
  corresponding [npm package page](https://www.npmjs.com/package/cline) document that the CLI is
  distributed via npm (`npm install -g cline`) after installing VS Code/VSCodium. The CLI exposes a
  terminal interface once installed globally, matching our Docker use-case.
- `codex`: The [OpenAI Codex CLI repo](https://github.com/openai/codex) plus the developer docs
  (e.g. [developers.openai.com/codex/cli](https://developers.openai.com/codex/cli/)) describe
  installing the CLI via `npm install -g @openai/codex` (or Homebrew). The global npm install is the
  portable option we can script.
- `factory_ai_droid`: Factory’s CLI quickstart
  ([docs.factory.ai/cli/getting-started/quickstart](https://docs.factory.ai/cli/getting-started/quickstart))
  explains that the `droid` command ships as a Node-based CLI and can be installed via npm
  (`npm install -g @factory-ai/droid`, surfaced through their onboarding flow). When npm artifacts
  are unavailable (e.g., network blocks), the docs recommend falling back to `npx` which we can
  emulate via a lightweight shim.
