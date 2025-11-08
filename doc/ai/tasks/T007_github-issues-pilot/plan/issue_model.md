# T007 Issue Model Decisions

## Issue Template Highlights
- Template path: `.github/ISSUE_TEMPLATE/task.yml` (GitHub form).
- Required fields: Task ID (`T###`), slug/folder, context, goals, GitHub↔local links, sync plan, confirmations.
- Optional fields capture guardrails and Feedback so GitHub retains high-level history while the repo plan hosts execution detail.
- Default labels applied on creation: `task`, `status:proposed`.

## Label Taxonomy
| Label | Purpose | Color suggestion |
|-------|---------|------------------|
| `task` | Denotes canonical task-tracking issues. | `#1f6feb` |
| `status:proposed` | New/queued tasks (default). | `#6e7781` |
| `status:active` | Exactly one task at a time; mirrors task table “Active”. | `#2da44e` |
| `status:blocked` | Task paused pending input. | `#d29922` |
| `status:needs-review` | Task work ready for review/merge. | `#bf3989` |
| `status:completed` | Task fully merged/closed; close issue after marking. | `#8250df` |

_Operational notes_
- Update labels whenever the local plan’s Master Checklist crosses major gates. Example: flip to `status:active` when the plan folder exists; swap to `status:completed` only after merging into `development` and archiving subtasks.
- Keep exactly one `status:*` label per task issue so dashboards stay simple.

## Linking Policy
1. **Issue → Repo**
   - Include direct links (no pasted transcripts) to `doc/ai/tasks/T###_<slug>/README.md`, the plan README, and any research logs.
   - List branch names (`task/...`, `subtask/...`) and the latest checkpoint commit if useful for reviewers.
2. **Repo → Issue**
   - `doc/ai/tasks/README.md` table: Status column uses bold **Active** for the issue currently labeled `status:active`, and the Notes column links to both the task README and the GitHub issue URL once available.
   - Task-level README front matter (“Status” block) lists the GitHub issue as canonical scope plus the owner and plan link.
   - Each plan (task-level + subtasks) includes a “References” entry pointing back to the GitHub issue so offline agents know where to sync updates when back online.
3. **Progress Sync**
   - When updating plan checklists or logs, add a short GitHub issue comment summarizing the same checkpoint (include timestamp). If working offline, draft the comment in the plan Progress Log and post once online.

## Offline Fallbacks
- Continue updating local plan + Feedback sections as source of truth when disconnected.
- Before reconnecting, prepare a summary comment referencing the timestamps already logged locally; once online, paste to the GitHub issue so history stays aligned.
- If an issue cannot be created immediately (e.g., permission problems), note this in the plan Progress Log and revisit in S003.

## Open Considerations
- Subtasks currently stay local; revisit after evaluating the pilot.
- Automated label syncing could be scripted later; for now manual updates are acceptable but must be logged in the plan’s Feedback sections.
