# Task T009 / Subtask S003 — Author README + AGENTS Kickstart Flow

## Objective
Write the template’s README and AGENTS instructions so new users/agents can bootstrap a real project (README creation, AGENTS merge) assuming AGENTS.md support is available.

## Deliverables
- Template README describing how to use the project (AGENTS-first flow, human-readable overview only).
- Minimal AGENTS.md that detects kickstart mode and guides the agent to help the user produce real README + AGENTS content.
- Stripped “template AGENTS” reference file containing reusable workflow guidance.
- Checklist + Feedback updates.

## Flow
1. Based on S002 structure, draft the README (explain template nature, steps 1–2, and point humans toward AGENTS.md for full workflow).
2. Author the minimal AGENTS.md (kickstart instructions, mention MCP servers, etc.).
3. Produce the template AGENTS reference, retaining general workflow rules but removing project-specific details.
4. Cross-check instructions for clarity + brevity.
5. Commit `T009/S003: author kickstart instructions` once finished.

## Deliverable Notes
- **README.md** — Describes template purpose, a five-step quickstart checklist, and a table of included files. Encourages copying plan templates, syncing GitHub issues, and logging research under `doc/ai/research/` when applicable.
- **AGENTS.md** — Minimal “kickstart mode” guide that instructs agents to gather goals, create the first plan folder, customize docs, and remove the temporary guidance once a real AGENTS exists.
- **AGENTS.reference.md** — Portable workflow rules covering planning, GitHub issues/PRs, branch discipline, catalog hygiene, tooling/testing expectations, and feedback loops. Designed for copy/paste into the eventual project AGENTS with light edits.
- **doc/ai/tasks/README.md** — Task index scaffold with instructions for numbering, maintaining statuses, and mirroring progress to PRs.
- **Supporting files** — `.github/ISSUE_TEMPLATE/task.yml`, plan templates, and `.gitignore` copied in so the template is repo-complete on first clone.

## File Touchpoints
| File | Key Sections |
|------|--------------|
| `submodules/workflow-ready-template/README.md` | Overview, Quickstart Checklist, Template Contents table, customization + research guidance. |
| `submodules/workflow-ready-template/AGENTS.md` | Immediate actions for agents, working agreements, and hand-off expectations until a real AGENTS replaces it. |
| `submodules/workflow-ready-template/AGENTS.reference.md` | Workflow hardening, branch/commit policy, catalog expectations, testing/tooling, and feedback norms. |
| `submodules/workflow-ready-template/doc/ai/tasks/README.md` | Task table stub plus instructions for creating new task folders/issues. |

## Checklist
- [x] README drafted (template usage instructions).
- [x] Kickstart AGENTS.md drafted.
- [x] Template AGENTS reference drafted.
- [x] Feedback updated.
- [x] Commit `T009/S003: author kickstart instructions`.

## Inputs & References
- S001/S002 decisions.
- Existing AGENTS workflows.

## Exit Criteria
- Template docs ready for inclusion in the new repo/submodule.

## Feedback & Learnings
- **Open Problems**: Consider adding a `doc/ai/research/README.md` stub in the template if multiple teams request it; for now the README simply suggests creating it ad hoc.
- **Questions**: None; awaiting user review of the submodule files before iterating further.
- **Learnings**: Keeping AGENTS in a two-layer approach (kickstart vs. reference) makes it obvious when the repo graduates from template mode.
