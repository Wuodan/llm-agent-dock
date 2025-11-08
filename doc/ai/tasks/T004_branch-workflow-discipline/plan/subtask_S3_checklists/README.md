# Task T004 / Subtask S3 — Checklist & Template Propagation

## Objective
Update task and subtask planning templates (and any other reusable checklists) so that the new branching workflow steps become part of every future effort.

## Deliverables
- Revised `doc/ai/templates/task_plan_README.template.md` and `doc/ai/templates/subtask_plan_README.template.md` as needed to mention branch workflow checkpoints.
- Any additional checklist snippets (e.g., doc/ai/tasks/README instructions) referencing the process.
- Updated plan + Feedback entries capturing what changed and outstanding follow-ups.
- 2025-11-08 scope update: templates must also enforce the new commit subject prefix (`T###/S###: short summary`). Document rationale and instructions wherever the commit step appears.

## Template Changes
- `task_plan_README.template.md`: Guardrail #4 now specifies the `T###/S###:` commit format (with `S000` guidance) so task plans propagate the new requirement.
- `subtask_plan_README.template.md`: Flow/checklist bullets updated to reference the same prefix whenever commits are mentioned.
- Legacy task/subtask docs inherit the policy through manual updates in S2; future tasks will rely on these template defaults.

## Flow
1. Review S1 decisions and AGENTS.md updates to identify which parts must be enforced via templates vs. referenced as links.
2. Update template sections (workflow guardrails, checklist bullets) to include branch creation/push/merge steps and reminders to log commands/tests.
3. Verify that templated checklists still fit within AGENTS.md expectations (objective/deliverables/flow/feedback).
4. No automated tests required; proofread Markdown and ensure placeholders remain clear.
5. Update plan checklist + Feedback as progress is made.
6. Commit `T004/S003: summary` once the templates and docs are updated.

## Checklist
- [x] Identify every template/checklist that needs branch workflow + commit-prefix references.
- [x] Apply updates ensuring placeholders remain generic yet prescriptive.
- [x] Cross-check against AGENTS.md to prevent conflicting guidance.
- [x] Document findings in Feedback.
- [x] Commit `T004/S003: summary`.

## Inputs & References
- `doc/ai/templates/task_plan_README.template.md`
- `doc/ai/templates/subtask_plan_README.template.md`
- `doc/ai/tasks/T004_branch-workflow-discipline/plan/subtask_S1_branch-policy/README.md`
- `doc/ai/tasks/T004_branch-workflow-discipline/plan/subtask_S2_doc-updates/README.md`

## Exit Criteria
- Templates include the new workflow steps, plan feedback updated, and references validated.

## Feedback & Learnings
- **Open Problems**: Need to audit older task folders periodically to ensure they re-copy the updated templates instead of cloning stale ones.
- **Questions**: Should we supply a canned example (e.g., `T999/S001: ...`) in the templates, or leave it implied by AGENTS? Currently leaning toward short example in plan guardrails.
- **Learnings**: Embedding the commit format directly into templates prevents regressions when new tasks are scaffolded without re-reading AGENTS.md.
