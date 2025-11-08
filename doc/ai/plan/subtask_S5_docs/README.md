# Subtask S5 — Documentation & Polish

## Objective
Align all written guidance with the implemented build system so newcomers can understand the matrix,
run commands, extend bases/tools, and trace decisions via planning docs.

## Deliverables
- Updated root `README.md` (user-facing only) covering:
  - Concise overview + value prop.
  - Matrix table (bases/tools/platforms) and quick-start commands.
  - Extension guidance for adding bases/tools.
  - Pointer to contributor docs (`AGENTS.md`, `doc/ai/plan/`) without embedding process detail.
- Supporting contributor docs (if any) live under `doc/ai/` and reference the plan as needed.
- Finalized plan docs reflecting completion (checklists + feedback).

## Flow
1. Audit actual implementation artifacts (Dockerfile, Bake file, scripts, tests).
2. Update README sections (goal, architecture, commands, extension steps, testing) while keeping the
   tone user-centric.
3. Ensure plan + subtask docs reference final states and include lessons learned.
4. Proofread for clarity and alignment with AGENTS.md style (tables, ~100-char lines).
5. Commit `[codex][docs]: refresh usage + extension guide]`.

## Checklist
- [x] Architecture + matrix documentation refreshed.
- [x] Commands section synced with `scripts/`.
- [x] Extension guidance updated (add base/tool instructions).
- [x] Testing instructions reference `scripts/test.sh` and smoke suites.
- [x] Plan + feedback sections finalized.
- [x] Commit `[codex][docs]: refresh usage + extension guide]`.

## Inputs & References
- Outputs of S2–S4.
- Existing README content.

## Exit Criteria
- Documentation matches repo state and guides future contributors.

## Feedback & Learnings
- README now highlights configuration defaults, Bake automation, and smoke-test usage so operators
  can move from bootstrap → build → test without digging through scripts.
- Testing guidance calls out the `bats` dependency up front, preventing the missing-binary issue
  encountered during S4 verification attempts.
