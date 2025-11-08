# Task T003 / Subtask S3 — Agent Startup Capture

## Objective
Launch each agent CLI (`cline`, `codex`, `factory_ai_droid`) inside every supported base image (`ubuntu`, `act`, `universal`), observe startup prompts, and capture stdout/stderr behavior for CI-safe automation.

## Deliverables
- Reproduction commands (docker run/build/test invocations) per agent/base combo, documented in this subtask plan.
- Sanitized log snippets noting timing, prompts, auth requirements, and blocking conditions.
- Inventory of missing packages, required env vars, or config files uncovered during runs.
- Feedback entries summarizing issues + recommendations feeding S4.

## Flow
1. Build or pull the relevant agent images using `docker buildx bake` or `scripts/build.sh <tool> <base>` (respecting platform constraints noted in S2).
2. Start each container with non-interactive wrappers (e.g., `docker run --rm -i` with `script`/`stdbuf` or `pexpect` helper) to capture stdout/stderr asynchronously; log command + location of saved logs.
3. Document prompts/auth flows encountered; attempt bypass via env vars or placeholders without entering real credentials.
4. Note any missing dependencies or file paths; triage whether Dockerfile/test updates are needed.
5. Update checklists + Feedback, then commit `[codex][subtask-S3_agent_startup_tests]: summary` once all combos are covered or blockers recorded.

## Observations & Logs
- Harness: added `scripts/dev/capture_agent_startup.py` (async stdout/stderr taps, optional PTY support, env injection, log fan-out into `doc/ai/tasks/T003_intensive-startup-tests/plan/logs/`). Example: `scripts/dev/capture_agent_startup.py codex ubuntu --pty --timeout 10` stores `startup_codex_ubuntu_<timestamp>.log`.
- Build outputs captured under `plan/logs/build_<tool>_<base>.log`; universal variants failed consistently with `ghcr.io/devcontainers/images/universal:2-linux` 403 (needs GH auth token) so only `act` + `ubuntu` bases are available locally.
- Node baseline inside all images is v18.19.1; `cline` startup requires Node ≥20 to launch its core process (fails before auth prompts). Logs: `startup_cline_ubuntu_20251108T050915Z.log`, `startup_cline_act_20251108T050932Z.log`.
- `codex` interactive CLI refuses non-TTY stdout; PTY mode plus Device Status Report replies are necessary. Default invocation either errors (`startup_codex_ubuntu_20251108T050947Z.log`) or renders control-code-only TUI buffers (`startup_codex_act_20251108T051409Z.log`), while `codex login` prints OAuth instructions and localhost callback URLs (`startup_codex_ubuntu_20251108T051341Z.log`, `startup_codex_act_20251108T051423Z.log`).
- `factory_ai_droid` immediately installs 15 templates into `~/.factory` (personal scope) even without arguments; stdout guidance logged in `startup_factory_ai_droid_ubuntu_20251108T051447Z.log` and `startup_factory_ai_droid_act_20251108T051454Z.log`. Tests should run with `--dry-run` or snapshot home directories to avoid polluting CI nodes.

### Build Status Snapshot (2025-11-08)
| Target | Result | Notes |
|--------|--------|-------|
| cline-ubuntu | ✅ built via `scripts/build.sh` | Logs: `build_cline_ubuntu.log` |
| cline-act | ✅ | `build_cline_act.log` |
| cline-universal | ❌ | GHCR 403 pulling `devcontainers/images/universal:2-linux` |
| codex-ubuntu | ✅ | `build_codex_ubuntu.log` |
| codex-act | ✅ | `build_codex_act.log` |
| codex-universal | ❌ | Same GHCR 403 |
| factory_ai_droid-ubuntu | ✅ | `build_factory_ai_droid_ubuntu.log` |
| factory_ai_droid-act | ✅ | `build_factory_ai_droid_act.log` |
| factory_ai_droid-universal | ❌ | Same GHCR 403 |

### Agent Findings (per base)
- **Cline**
  - Default `cline` command crashes immediately because bundled “core” downloader insists on Node ≥20; our images ship Debian Node v18.19.1. Until Node is upgraded (NodeSource/Volta), startup tests will always fail before auth prompts; `cline version` succeeds but interactive sessions die (logs linked above).
  - No auth prompt observed yet—CLI never reaches provider selection due to Node gate.
- **Codex**
  - `codex` (no args) launches a full-screen TUI that only emits control codes; log capture requires PTY mode plus Device Status Report (DSR) replies. Without PTY the CLI exits with `stdout is not a terminal`.
  - `codex login` opens a local HTTP server on `http://localhost:1455` and prints a browser OAuth URL (see `startup_codex_*_...1341Z.log`). This flow cannot complete inside CI unless we preload credentials (e.g., `~/.codex/config.toml`) or stub the HTTP callback.
  - Suggestion: pipe an API key via `printf "$OPENAI_API_KEY" | codex login --with-api-key` before automation, then run `codex exec`/`codex task` non-interactively.
- **Factory AI Droid**
  - Command runs non-interactively, emits success banner, and writes templates into `~/.factory/{commands,droids}`. No auth prompt.
  - Re-running duplicates work unless `--dry-run` or `--force` toggles are supplied. Tests need to run in disposable HOME directories to avoid residue.

### Log Inventory (2025-11-08 run)
- Startup captures: `plan/logs/startup_{cline,codex,factory_ai_droid}_{act,ubuntu}_*.log`
- Build logs: `plan/logs/build_<tool>_<base>.log`
- Harness script: `scripts/dev/capture_agent_startup.py`

## Checklist
- [x] All agent/base combos exercised or explicitly blocked with rationale.
- [x] Logs + observations saved under `plan/` with timestamps.
- [x] Auth prompt handling + env var strategy documented.
- [x] Missing dependency list captured.
- [x] Document findings in Feedback.
- [x] Commit `[codex][subtask-S3_agent_startup_tests]: summary`.

## Inputs & References
- Scripts under `scripts/`.
- Task README + subtask S2 environment notes.
- Existing `tests/smoke/*.bats` for reference on invocation patterns.

## Exit Criteria
- Each agent/startup scenario evaluated with reproducible commands, logs stored, and Feedback summarizing outstanding failures or follow-ups.

## Feedback & Learnings
- **Open Problems**:
  - Need Node.js 20+ in every base to allow `cline` core to start; decide between NodeSource install vs. copying upstream release tarballs.
  - `codex` login requires real browser OAuth on localhost:1455; need a CI-safe credential seeding method (pre-populated config or service tokens).
  - Universal base builds blocked by GHCR 403 on `devcontainers/images/universal:2-linux`; requires PAT or alternative mirror.
- **Questions**:
  - Are we allowed to store dummy `.codex/config.toml` with pre-issued API tokens in the image, or should tests inject secrets via env vars?
  - Should `factory_ai_droid` be invoked with `--list`/`--dry-run` for smoke tests to avoid altering `$HOME`?
- **Learnings**: PTY-based capture (plus responding to ANSI `ESC[6n`) stabilizes codex logs; `factory_ai_droid` installs templates immediately, so running inside disposable homes is mandatory.
