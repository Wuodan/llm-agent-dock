# Task T004 / Subtask S4 — Commit Prefix Lint Enforcement

## Objective
Provide an automated guardrail (hook + script) that blocks commits whose subject lines do not match the required `T###/S###: short summary` format.

## Deliverables
- A tracked hook or script (e.g., `githooks/commit-msg` + helper under `scripts/`) that validates commit subjects locally.
- Documentation updates (AGENTS.md or README) explaining how to enable the hook and how CI/agents can run the lint manually.
- Updated plan + Feedback entries summarizing the enforcement mechanism and any follow-up needs.

## Flow
1. Design a lightweight checker (bash or python) that verifies the first line matches `^T\d{3}/S\d{3}: ` and fails otherwise; ensure it exits non-zero on violations.
2. Place the script under a tooling directory (not `scripts/`) and wire a `githooks/commit-msg` wrapper that calls it. Document enabling instructions (`git config core.hooksPath githooks`).
3. Update AGENTS.md (or relevant docs) with a short section on installing hooks and running the checker manually.
4. Test locally by crafting temp commit messages (use `.venv/bin/python devtools/check_commit_message.py --message ...` or `git commit --allow-empty`) and capture results in this plan.
5. Update checklist + Feedback, then commit `T004/S004: summary` once the lint and docs are in place.

## Implementation Notes
- Added `devtools/check_commit_message.py` (Python, runs under `.venv`) that can read either a file path or a `--message` arg; pattern enforced is `^T[0-9]{3}/S[0-9]{3}: ` with trailing text required.
- Tracked `githooks/commit-msg` invokes `.venv/bin/python devtools/check_commit_message.py`; contributors enable it with `git config core.hooksPath githooks` and by activating `.venv` beforehand.
- Documentation refreshed: AGENTS.md now explains the hook + manual command, README gained a "Commit Prefix Hook" section with `.venv` usage, and prerequisites call out activating the venv before running helper scripts.

### 2025-11-08 Scope Update
- User requested the linter move out of `scripts/` (reserved for production helpers/tests) and leverage the new `.venv` Python interpreter. Need to re-implement the checker in Python under a tooling-specific directory (e.g., `devtools/`), update hooks/docs to reference `.venv/bin/python`, and expand README/AGENTS with venv instructions.

## Testing
- `.venv/bin/python devtools/check_commit_message.py --message "T004/S004: lint hook"` exits 0 (valid).
- `.venv/bin/python devtools/check_commit_message.py --message "fix subject"` exits 1 and prints guidance.
- Verified the hook script resolves repo root using `git rev-parse --show-toplevel` so it works from subdirectories and prefers `.venv/bin/python` with a fallback to system `python` if necessary.

## Checklist
- [x] Implement reusable commit-message checker script.
- [x] Add tracked git hook + docs explaining how to enable/run it.
- [x] Manually test valid/invalid commit messages and note results.
- [x] Document findings in Feedback.
- [x] Commit `T004/S004: summary`.
- [x] Migrate checker to Python under non-production tooling dir.
- [x] Update hook/docs to reference `.venv/bin/python` + new location.
- [x] Re-run manual tests and record results.
- [ ] Commit `T004/S004: python lint update`.

## Inputs & References
- `AGENTS.md`
- `doc/ai/tasks/T004_branch-workflow-discipline/plan/README.md`
- Existing repo scripts/hooks for style inspiration (none yet).

## Exit Criteria
- Checker + hook exist, docs updated, tests executed, and plan Feedback captures any follow-ups.

## Feedback & Learnings
- **Open Problems**: Could add a CI job to run `.venv/bin/python devtools/check_commit_message.py --message "$(git log -1 --pretty=%s)"` on PR heads to double-check remote pushes; future work if CI hooks become available.
- **Questions**: For contributors unable to change `core.hooksPath`, should we document running the script via `prepare-commit-msg` alternative? Pending feedback from users of platforms with restricted hooks.
- **Learnings**: Keeping the script under `scripts/` lets both hooks and CI share logic, avoiding divergence.
