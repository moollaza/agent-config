# Workflow Skills Map

When tackling non-trivial work, prefer invoking installed skills over freeform prose. The matrix below lists the canonical skill for each phase, the trigger to invoke it, and what it produces.

## Skill matrix

| Phase | Skill | Trigger | Produces |
|---|---|---|---|
| Frame | `compound-engineering:ce-brainstorm` | Requirements fuzzy; user wants to think out loud. | Right-sized requirements doc. |
| Frame | `improve-codebase-architecture` (Matt) | Want plan grounded in codebase domain language and ADRs (`CONTEXT.md` + `docs/adr/`). | Architectural deepening opportunities. |
| Plan | `compound-engineering:ce-plan` | Convert resolved context into a plan-of-record. | Project plan document. |
| Plan | `to-prd` (Matt) | Convert resolved context into a PRD; publishes to **Linear** (per Agent Skills config in CLAUDE.md). | Product requirements doc as Linear issue. |
| Stress-test | `grill-me` (Matt) | Before implementing a non-trivial plan; user says "stress test", "poke holes", "grill me". | Open decisions resolved one branch at a time. |
| Stress-test | `grill-with-docs` (Matt) | Same as `grill-me` but plan needs to align with codebase docs/ADRs. | Resolved plan informed by codebase context. |
| Track | `to-issues` (Matt) | Convert PRD into vertical-slice **Linear** issues (per Agent Skills config in CLAUDE.md). | One issue per slice, ready to implement. |
| Track | `triage` (Matt) | Sweep the **Linear** backlog into actionable tasks. | Prioritized, labeled issue list. |
| Build | `tdd` (Matt) | Feature with testable behavior; want red-green-refactor. | Tests-first implementation. |
| Build | `compound-engineering:ce-work` | Standard end-to-end implementation loop. | Implemented + verified change. |
| Review | `compound-engineering:ce-review` | Multi-agent code review of pending changes. | Review report. |
| Review | `argos-pr-review` | PR has Argos check that's red, pending, or `changes-detected`. | Visual-regression triage. |
| Document | `compound-engineering:ce-compound` | Just solved a non-obvious problem; want institutional memory. | Documented learning for the team. |
| Personal workflow | `zm:plan` / `zm:research` / `zm:implement` / `zm:review` / `zm:cleanup` / `zm:handoff` / `zm:resume-handoff` | Personal end-to-end loop. | Per-step artifacts. |

## How to choose between similar skills

- **`ce-plan` vs `to-prd`**: `to-prd` produces a PRD for a feature; `ce-plan` produces a project plan for execution. Big features may want both (PRD → plan).
- **`grill-me` vs `grill-with-docs`**: Use `grill-with-docs` when the codebase has a `CONTEXT.md` or `docs/adr/` and the plan needs to reflect them; it updates those docs inline as decisions crystallize. Otherwise `grill-me`.
- **`ce-work` vs `tdd`**: `tdd` for behavior-testable features (logic, transforms). `ce-work` for end-to-end implementation that includes UI, infra, or non-test-driven changes.
- **`to-issues` vs `triage`**: `to-issues` is forward (PRD → issues). `triage` is backward (existing chaos → issues).

## Default sequence for a sizable feature

1. `ce-brainstorm` → resolve requirements.
2. `to-prd` (or `ce-plan`) → write it down.
3. `grill-me` (or `grill-with-docs`) → stress-test before implementing.
4. `to-issues` → carve into vertical slices.
5. `tdd` (or `ce-work`) → implement each slice.
6. `ce-review` → review.
7. `ce-compound` → capture any non-obvious lessons.

For small fixes, skip to step 5 directly via `zm:quick-fix` or `ce-work`.

## When to NOT invoke a skill

- The task is genuinely trivial (typo, comment, single-line config bump).
- The user has asked for a specific approach — follow that, don't second-guess via skill.
- A skill would slow the loop without changing the outcome.

## Discovery

If the user describes a task that doesn't obviously match a skill, run the `find-skills` skill to surface candidates before doing freeform work.
