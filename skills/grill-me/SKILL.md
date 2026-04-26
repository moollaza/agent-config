---
name: grill-me
description: >
  Stress-test a plan or design by interviewing the user relentlessly until reaching shared understanding.
  Use when the user says "grill me", "stress test this plan", "poke holes in this", "challenge my design",
  or after completing a plan to ensure it survives scrutiny. Walks each branch of the decision tree,
  resolving dependencies between decisions one by one.
---

# Grill Me

Interview the user relentlessly about every aspect of their plan or design
until reaching shared understanding. Walk down each branch of the decision
tree, resolving dependencies between decisions one by one.

## Rules

1. **Explore the codebase first.** If a question can be answered by reading
   code, configs, or docs — do that instead of asking the user. Only ask
   questions that require human judgment or context you can't find.

2. **One branch at a time.** Don't shotgun 10 questions. Pick the most
   critical open branch, resolve it fully, then move to the next.

3. **Recommend an answer.** For every question, provide your recommended
   answer with brief reasoning. The user can accept, reject, or refine.

4. **Be adversarial, not hostile.** Challenge assumptions, surface edge cases,
   find contradictions — but stay constructive. The goal is a better plan,
   not a demolished one.

5. **Track what's resolved.** Maintain a running list of resolved decisions
   and open branches so the user can see progress.

6. **Know when to stop.** When all branches are resolved and you've run out
   of meaningful challenges, summarize the resolved decisions and declare
   the plan grilled.

## Flow

### Phase 1: Understand the Plan

Read the plan or design document thoroughly. If no document exists, ask the
user to describe what they're planning.

Identify the major decision branches:
- Architecture choices
- Scope boundaries
- Technical tradeoffs
- Assumptions that could be wrong
- Missing error/edge cases
- Dependencies and ordering

### Phase 2: Grill

For each branch, starting with the highest-risk one:

```
**Branch: [topic]**

[Context from your reading of the plan/codebase]

**Question:** [specific, pointed question]

**My recommendation:** [your suggested answer + reasoning]
```

Wait for the user's response. Once resolved, mark it and move on.

### Phase 3: Summary

When all branches are resolved:

```
## Grill Complete

### Resolved Decisions
- [Decision 1]: [resolution]
- [Decision 2]: [resolution]
- ...

### Changes to Make
- [Any plan updates that came out of the grilling]

### Confidence
[Your honest assessment of the plan's readiness]
```
