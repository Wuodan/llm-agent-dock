# Task T009 / Subtask S002 — Template Structure & Contents

## Objective
Decide which files/folders belong in the kickstart template (README, minimal AGENTS, template AGENTS reference, scripts if any) without bringing project-specific code.

## Deliverables
- File/folder map showing what the template repo contains at initialization.
- Justification for included tools (e.g., virtualenv script, linting pointers) or explicit rationale if omitted.
- Checklist + Feedback updates.

## Flow
1. Review current repo structure and identify reusable elements.
2. Propose a minimal set of files (README, AGENTS, template AGENTS, optional helper scripts).
3. Validate against “no empty dirs / no unnecessary placeholders”.
4. Document decisions for S003 authoring.
5. Commit `T009/S002: define template structure` after checklist complete.

## Proposed Structure
| Path | Purpose | Notes |
|------|---------|-------|
| `README.md` | Quickstart for humans + agents to clone, rename, and wire their project | Will outline setup steps, task catalog expectations, links into AGENTS.
| `AGENTS.md` | Canonical workflow guardrails in condensed form | Derived from this repo’s AGENTS but scoped to template-friendly instructions.
| `doc/ai/tasks/README.md` | Task catalog scaffold so teams can immediately log T### rows | Keeps “one active task” rule; links back to templates + issue tracker.
| `doc/ai/templates/task_plan_README.template.md` | Task planning template | Copied from this repo for continuity.
| `doc/ai/templates/subtask_plan_README.template.md` | Subtask planning template | Same as above; ensures plan scaffolding ships with template.
| `.github/ISSUE_TEMPLATE/task.yml` | Standardized GitHub issue form for tasks | Ensures GitHub→plan parity from day one.
| `.gitignore` | Ignore Python venvs, `.DS_Store`, etc. | Keeps repo clean without forcing tooling choices.

### Optional/Deferred Elements
- `scripts/` helpers intentionally omitted: until we decide on a universal bootstrap story, the template should stay documentation-first. Future tasks can add scripts once requirements stabilize.
- Sample task folders (e.g., `T000_example`) omitted to avoid stale pseudo-content; README will instruct users to create T### as needed.

## Tooling Decisions
- **No executable helpers yet**: Documenting the AGENTS workflow + templates provides the most leverage; adding shell scripts would imply opinionated environments we haven’t validated across consumers.
- **Include `.gitignore`**: Prevents accidental commit of local env files while remaining neutral.
- **Ship GitHub issue template**: Keeps issue/plan symmetry without requiring extra setup after cloning.

## Checklist
- [x] File/folder plan drafted.
- [x] Tooling decisions recorded.
- [x] Feedback updated.
- [x] Commit `T009/S002: define template structure`.

## Inputs & References
- Outputs from S001.
- Current AGENTS.md best practices.

## Exit Criteria
- Clear structure ready for content authoring.

## Feedback & Learnings
- **Open Problems**: Need to confirm whether the template should vend a starter task folder (e.g., `T001_sample`) or rely solely on docs—current leaning is docs only, but revisit if onboarding feedback says otherwise.
- **Questions**: Should we include a `doc/ai/research/README.md` stub to capture shared research logs, or is that overkill for v1?
- **Learnings**: Separating structure rationale (table) from tooling decisions keeps future edits scoped; reuse this layout for other template-definition subtasks.
