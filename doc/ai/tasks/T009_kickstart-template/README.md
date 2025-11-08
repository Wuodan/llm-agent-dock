# Task T009 — Project Kickstart Template

## Status
- Status: Proposed (pending naming decisions)
- Owner: TBD
- Links: `doc/ai/tasks/T009_kickstart-template/plan/README.md`

## Background
We want to capture our workflow in a reusable GitHub template so new projects can start with the same AGENTS/README structure. The template should ship with concise instructions guiding the user (and their coding agent) through creating a project-specific README and merging workflow guardrails.

## Goals & Deliverables
1. Collaboratively choose the template repo name, one-line GitHub description, and submodule path.
2. Define which files belong in the template (initial README, minimal AGENTS.md, template AGENTS reference, any helper scripts).
3. Author the template README + AGENTS instructions so users can bootstrap their real project (agent-assisted flow plus manual fallback).
4. Add the new repo as a submodule inside this repo and document how to keep it updated.

## Out of Scope
- Duplicating this repo’s project-specific content or tooling beyond what’s reusable.
- Automating the template creation process; we’ll handle it manually for now.

## Dependencies & Inputs
- Outcomes from T008 (cost-aware workflow guardrails).
- Current AGENTS.md and README patterns.

## Open Questions
- Final repo name, description, and submodule path.
- Whether to include helper scripts (bootstrap, lint) in the template or leave it documentation-only.
- How much of the existing AGENTS content should the template inherit vs. recreate dynamically.

## Next Steps
- Finalize naming (S001) and then proceed through S002–S004 per the plan.
