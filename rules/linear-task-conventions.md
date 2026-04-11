---
description: "Conventions for creating, structuring, and executing Linear issues. Apply when creating, updating, or executing Linear issues — whether via MCP, ce:plan, ce:work, or ad-hoc."
alwaysApply: true
---

# Linear Task Conventions

---

## Organization

Use one team for all work. Teams map to groups of people, not products.

Use one Project per product or side project. Include a brief "what and why" in the Project description.

Use Milestones within Projects for major phases (e.g., "MVP", "Beta", "Launch") only when the project is large enough to warrant them.

---

## Issue Hierarchy

**Issues** represent a meaningful, reviewable unit of work — a feature, bug fix, or refactor. Not a single function change, not an entire epic.

**Sub-issues** break an Issue into implementable steps. Each sub-issue should be completable in a single Claude session (roughly one PR or one logical change).

Promote an Issue to a Project if it accumulates more than ~8 sub-issues.

---

## Title Format

Follow the pattern: `[Verb] [specific thing] [in/for scope]`

Use verb-first for scannability: Add, Fix, Refactor, Remove, Update, Extract, Replace.

Make titles specific enough to distinguish from siblings at a glance.

**Examples:**
- Add rate limiting to API endpoints
- Fix timezone handling in schedule export
- Extract payment logic into service object
- Remove deprecated webhook handler from notifications

---

## Description Templates

### Parent Issues

```
## Context
[1-3 sentences: what's happening, why this matters, relevant background]

## Done when
- [ ] [Concrete, verifiable acceptance criterion]
- [ ] [Concrete, verifiable acceptance criterion]

## Dependencies
[List Blocks and Blocked by relations with issue IDs, or "None"]

## Notes for execution
[Hints for Claude: which parts are independent, relevant files/patterns, testing approach, constraints]
```

### Sub-Issues

Use a lighter template — context is inherited from the parent:

```
## Done when
- [ ] [Concrete, verifiable acceptance criterion]

## Notes for execution
[Only if needed: specific files, edge cases, or constraints not obvious from parent]
```

### Verifiability Rule

"Done when" criteria must be verifiable. A human or AI can look at the result and confirm yes/no. Do not use vague criteria like "works well" or "is clean."

**Good:** "API returns 429 status with retry-after header when rate limit exceeded"
**Bad:** "Rate limiting works properly"

---

## Parallelism and Dependencies

**Independent sibling sub-issues** (no Blocks/Blocked by between them) signal "these can run in parallel." Batch or parallelize these.

**Blocks/Blocked by relations** signal sequential execution order. Respect these.

Relations are the primary parallelism signal. When Linear MCP is not yet configured, "Notes for execution" serves as the fallback signal for parallelism (e.g., "Frontend and backend changes are independent"). Once MCP is live, relations are the source of truth and notes are supplementary.

**Example structure:**
```
Issue: Add user authentication
  ├── Sub: Add JWT middleware to API        (no relations → parallel)
  ├── Sub: Add login form to frontend       (no relations → parallel)
  └── Sub: Add end-to-end auth tests        (blocked by both above → sequential)
```

---

## Labels

Use a **Type** label group: `Feature`, `Bug`, `Chore`, `Refactor`.

Optionally use a **Scope** label group when the project spans distinct areas: `Frontend`, `Backend`, `Infra`, `Docs`.

Use priority levels (Urgent / High / Medium / Low) to signal execution order when dependencies alone do not capture it.

---

## Status Workflow

Keep the default workflow: Backlog > Todo > In Progress > Done > Canceled.

Move issues through statuses during execution: Todo → In Progress when starting, In Progress → Done when acceptance criteria are met. (Requires Linear MCP — until then, status updates are manual.)
