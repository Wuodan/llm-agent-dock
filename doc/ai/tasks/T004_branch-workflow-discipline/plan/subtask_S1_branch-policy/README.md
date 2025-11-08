# Task T004 / Subtask S1 — Branch Workflow Policy Decisions

## Objective
Select and document the authoritative branching workflow (naming, creation, push cadence, merge method, deletion rules, and force-push policy) that every task/subtask must follow.

## Deliverables
- Decision summary recorded in this subtask doc and referenced in the task plan Progress Log.
- Draft text snippets for AGENTS.md and templates reflecting the chosen policies.
- Updated plan + Feedback section with takeaways and unresolved questions.

## Flow
1. Review AGENTS.md, existing task templates, and notes from T001–T003 to understand current guidance and pain points.
2. Research lightweight Git workflow best practices if needed; log any external URLs + summaries in this doc.
3. Decide on branch naming conventions (task vs subtask), merge mechanism (GitHub PR vs local `git merge --no-ff`), push/force-push cadence, and deletion requirements.
4. Validate decisions against repository constraints (single active task, commit format, multi-agent hand-offs) and capture rationale.
5. Update this plan’s checklist and Feedback field each time progress is made; no automated tests required for this documentation-only subtask.
6. Commit `T004/S001: summary` once all checklist items are complete.

## Current Guidance Audit
- `AGENTS.md` documents planning, testing, and commit-format rules but omits branch naming, push cadence, force-push restrictions, and merge mechanics, which has allowed contributors to work directly on `development`.
- Task/subtask templates likewise lack instructions about switching off inherited branches, so someone can unknowingly continue on a stale branch.
- Notes from T001–T003 mention amend-last-commit habits but offer no guardrails, confirming the workflow gap is still unresolved.

## Branch Workflow Decisions
- **Hierarchy**: Maintain one task branch per active task named `task/T###_<slug>` (slug matches `doc/ai/tasks/` folder). All work for a subtask lives on `subtask/T###_S#_<slug>` created from the task branch tip. No commits land directly on `development`.
- **Creation/push flow**:
  1. `git checkout development && git pull --ff-only origin development` before branching a task.
  2. `git checkout -b task/T###_<slug>` (or `subtask/...` from the parent branch).
  3. Immediately `git push -u origin <branch>` so remote history reflects the new work in case of local failures.
- **Push cadence**: Push after branch creation, after meaningful checkpoints (tests, major edits), and before ending a session or hand-off. If you cannot push (offline), note it in the plan log and push at the next opportunity.
- **Merge mechanism**: Always merge locally with `git merge --no-ff`.
  - Subtasks: checkout the parent task branch, `git pull --ff-only origin <task>`, run validations, `git merge --no-ff subtask/...`, resolve conflicts, rerun checks, then `git push origin <task>`.
  - Tasks: once subtasks are integrated, checkout `development`, pull fast-forward, `git merge --no-ff task/...`, run validations, then push `development`.
- **Verification/deletion**: After pushing the parent branch, confirm the merge via `git log --oneline -1 origin/<parent>` and `git branch --merged`. Only then delete local and remote child branches (`git branch -d <branch>` and `git push origin --delete <branch>`). Update the plan checklist immediately.
- **Force-push policy**: Never force-push `development` or task branches. Subtask branches may be force-pushed only before another agent pulls them or to remove sensitive data; any exception must be recorded in the plan Feedback with rationale and follow-up steps.
- **Hand-off hygiene**: Before pausing, push both the subtask and parent branches, record outstanding work + branch names in the plan progress log, and ensure checklists reflect the latest state.

## Draft Snippets for Downstream Docs
- Branch naming: "Create task branches as `task/T###_<slug>` from `development`, and create subtask branches as `subtask/T###_S#_<slug>` from the task branch tip."
- Push discipline: "Push immediately after branch creation and after every checkpoint so remote history mirrors the plan progress log."
- Merge flow: "All merges happen locally via `git merge --no-ff`: subtasks merge into their task branch; tasks merge into `development`. Pull the parent with `git pull --ff-only` first, run required tests, then push the parent branch."
- Verification/deletion: "Only delete child branches after confirming the merge on both local and origin (`git branch --merged` + `git log --oneline origin/<parent>`). Delete the local branch and run `git push origin --delete <branch>`."
- Force-push rule: "Force pushes are prohibited on shared branches; limited exceptions on unpublished subtasks must be logged in the plan."

## Checklist
- [x] Audit current guidance and identify gaps.
- [x] Define naming + merge + push policies with rationale recorded here.
- [x] Provide draft wording / bullets for downstream docs.
- [x] Document findings in Feedback.
- [x] Commit `T004/S001: summary`.

## Inputs & References
- `doc/ai/tasks/T004_branch-workflow-discipline/README.md`
- `AGENTS.md`
- `doc/ai/templates/task_plan_README.template.md`
- `doc/ai/templates/subtask_plan_README.template.md`

## Exit Criteria
- Checklist is fully checked, Feedback updated, and decisions clearly written for reuse in S2/S3.

## Feedback & Learnings
- **Open Problems**: Automating branch name validation (pre-push hook or CI check) would prevent typos but is out of scope for this doc-only task.
- **Questions**: Should there be a reserved prefix for operational hotfixes outside the task system? Need repo-owner guidance.
- **Learnings**: Enforcing "one active task" simplifies the branch tree, but explicit naming + deletion steps are still necessary for smooth hand-offs.
