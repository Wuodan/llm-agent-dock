# Task T009 / Subtask S003 — Author README + AGENTS Kickstart Flow

## Objective
Write the template’s README and AGENTS instructions so new users/agents can bootstrap a real project (README creation, AGENTS merge) assuming AGENTS.md support is available.

## Deliverables
- Template README describing how to use the project (AGENTS-first flow, human-readable overview only).
- Minimal AGENTS.md that detects kickstart mode and guides the agent to help the user produce real README + AGENTS content.
- Full AGENTS.md copy containing the reusable workflow guidance (minus repo-specific tech sections).
- Checklist + Feedback updates.

## Flow
1. Based on S002 structure, draft the README (explain template nature, steps 1–2, and point humans toward AGENTS.md for full workflow).
2. Copy the parent repo’s AGENTS.md and remove tech-specific sections so it stays reusable across projects.
3. Ensure the supporting docs (task catalog, templates, issue form) align with the simplified approach.
4. Cross-check instructions for clarity + brevity.
5. Commit `T009/S003: author kickstart instructions` once finished.

## Deliverable Notes
- **README.md** — Human-facing instructions only with two explicit flows: (A) new project (fork or release tarball, rough README, prompt “help me improve README,” “help me update and complete AGENTS.md”), and (B) existing project (download tarball, copy everything except the README with sample Linux/macOS + Windows commands). Both paths finish with planning the first task and highlight the `.venv` prerequisite.
- **AGENTS.md** — Full copy of this repository’s AGENTS guidelines with only repo-specific technology references trimmed where needed; Python `.venv` expectations remain since the template now requires it.
- **doc/ai/tasks/README.md** — Task index scaffold with instructions for numbering, maintaining statuses, and mirroring progress to PRs.
- **Supporting files** — `.github/ISSUE_TEMPLATE/task.yml`, plan templates, `.gitignore`, and `devtools/check_commit_message.py` so teams can opt into the commit-subject hook immediately.

## File Touchpoints
| File | Key Sections |
|------|--------------|
| `submodules/workflow-ready-template/README.md` | Clone/fork instructions plus split guidance for new vs. existing projects. |
| `submodules/workflow-ready-template/AGENTS.md` | Repository-agnostic workflow guardrails (planning, branching, checklists) copied from the parent repo minus tech-specific sections. |
| `submodules/workflow-ready-template/doc/ai/tasks/README.md` | Task table stub plus instructions for creating new task folders/issues. |

## Checklist
- [x] README drafted (template usage instructions).
- [x] Kickstart AGENTS.md drafted.
- [x] AGENTS copy drafted (tech-specific sections removed).
- [x] Feedback updated.
- [x] Commit `T009/S003: author kickstart instructions`.

## Inputs & References
- S001/S002 decisions.
- Existing AGENTS workflows.

## Exit Criteria
- Template docs ready for inclusion in the new repo/submodule.

## Feedback & Learnings
- **Open Problems**: Consider shipping a `doc/ai/research/README.md` stub if adopters routinely ask for it (still deferred).
- **Questions**: None; previous draft discarded per user feedback, new version focuses on human-facing README + full AGENTS copy.
- **Learnings**: Simpler “single AGENTS file” reduces confusion—extra reference files felt redundant unless the owner explicitly asks for them.
