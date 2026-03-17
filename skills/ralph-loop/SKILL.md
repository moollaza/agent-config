---
name: ralph-loop
description: Use when the user wants to run autonomous iterative AI development loops, set up a Ralph Wiggum loop, or build a project with fresh-context-per-iteration agent cycles. Also use when the user mentions "ralph," "ralph loop," "autonomous loop," "iterative agent," "fresh context loop," or wants to let Claude work autonomously on a large task overnight. This skill covers the full workflow from specs to prompt generation to running the loop.
---

# Ralph Loop

Autonomous iterative development using fresh-context-per-iteration loops, based on Geoffrey Huntley's Ralph Wiggum technique.

**Source material:**
- [Original technique](https://ghuntley.com/ralph/) — Geoff Huntley's post
- [The Ralph Playbook](https://github.com/ghuntley/how-to-ralph-wiggum) — Reference implementation and detailed guide

## Core Concept

A bash while-true loop repeatedly feeds a prompt to Claude. Each iteration spawns a **fresh context** — memory persists only through the filesystem (`IMPLEMENTATION_PLAN.md`, `specs/`, `AGENTS.md`, git history). This prevents context decay and keeps every iteration in the smart zone.

```bash
while true; do
  claude -p --dangerously-skip-permissions --model opus < PROMPT_build.md
done
```

The bundled `loop.sh` adds iteration tracking, timing stats, signal handling, and mode switching on top of this core loop.

**Why fresh context matters:** With ~176K usable tokens and a 40-60% "smart zone," tight tasks + 1 task per loop = 100% smart zone utilization every iteration. A persistent session degrades over time as context fills.

**Key insight:** `IMPLEMENTATION_PLAN.md` persists on disk between iterations and acts as shared state between otherwise isolated loop executions. Each iteration loads the same files (`PROMPT.md` + `AGENTS.md` + `specs/*`) and reads current state from disk. No sophisticated orchestration needed — just a dumb bash loop that keeps restarting the agent.

## When to Use

- Large implementation tasks with clear specs (greenfield or major features)
- Tasks requiring 10+ iterations of autonomous work
- Well-defined success criteria (tests pass, plan complete)
- When you want Claude to work while you sleep

## When NOT to Use

- Quick fixes or single-file changes (use normal development)
- Tasks requiring constant human judgment or design decisions
- Debugging production issues (use systematic-debugging)
- Unclear requirements (do the spec conversation first)

## Three Phases, Two Prompts, One Loop

Ralph is a funnel with 3 phases, 2 prompts, and 1 loop.

### Phase 1 — Define Requirements (DO NOT SKIP)

Before any looping, have a thorough conversation about what you're building. Ralph is only as good as the specs it works from.

**REQUIRED SUB-SKILL:** Use `superpowers:brainstorming` to explore requirements.

Break the project into **Jobs to Be Done (JTBD)**, then decompose each JTBD into **topics of concern**. Each topic gets one spec file.

**Topic Scope Test — "One Sentence Without And":**
- Can you describe the topic in one sentence without conjoining unrelated capabilities?
- "The color extraction system analyzes images to identify dominant colors" — one topic
- "The user system handles authentication, profiles, and billing" — three topics

**Output:** A `specs/` directory with one markdown file per topic of concern:

```
specs/
  overview.md           # What we're building and why
  color-extraction.md   # One topic of concern
  image-collection.md   # Another topic of concern
  # ... one file per topic
```

Each spec should be detailed enough that an agent with no prior context can implement from it. If a spec is vague, ralph will make bad assumptions 20 times in a row.

**No pre-specified template** — let the LLM dictate format that works best. But include acceptance criteria: observable, verifiable outcomes that indicate success.

### Phase 2 — Generate Prompts & Scaffold

After specs are approved, **generate** project-specific prompt files. The skill bundles a reusable `loop.sh`, but the prompts must be crafted for each project.

**Put ralph files in a `ralph/` folder** to avoid cluttering the project root:

```
ralph/
  loop.sh
  PROMPT_plan.md
  PROMPT_build.md
AGENTS.md                       # stays at root — prompts reference @AGENTS.md
IMPLEMENTATION_PLAN.md          # stays at root — shared state between iterations
specs/                          # stays at root for visibility
  overview.md
  ...
```

**Explore the project first:**
- What's the directory structure? (Not always `src/*`)
- What build/test/lint commands does this project use?
- What shared utilities or patterns already exist?
- What's the tech stack?

**Generate these files and present each to the user for review:**

#### `PROMPT_plan.md`

Must follow this structure:

**Phase 0 (Orient):** Study specs and existing code with parallel subagents
- "Study `specs/*` with up to 250 parallel Sonnet subagents"
- "Study @IMPLEMENTATION_PLAN.md (if present)"
- "Study shared utilities/components with subagents"
- Reference correct source paths for this project

**Phase 1 (Analyze):** Gap analysis — specs vs code
- Use up to 500 Sonnet subagents to compare code against specs
- Use Opus subagent for analysis, prioritization, and plan generation
- Search for: TODOs, minimal implementations, placeholders, skipped tests, inconsistent patterns
- "Ultrathink"

**Hard constraints:**
- "Plan only. Do NOT implement anything."
- "Do NOT assume functionality is missing; confirm with code search first."

**Ultimate goal:** The project's specific goal — what are we building and why.

#### `PROMPT_build.md`

Must follow this structure:

**Phase 0 (Orient):** Study specs and plan with parallel subagents

**Phase 1-4 (Work → Validate → Commit):**
1. Pick highest-priority item from plan, search codebase first
2. Implement and run tests. "If functionality is missing, it's your job to add it."
3. Update plan with discoveries. When resolved, remove the item.
4. When tests pass, update plan, `git add -A`, `git commit`

**Subagent limits (critical):**
- Up to 500 parallel Sonnet subagents for searches/reads
- Only 1 Sonnet subagent for build/tests (prevents backpressure failures)
- Use Opus subagents when complex reasoning is needed (debugging, architecture)

**Signs (numbered invariants):** Include these defaults, add project-specific ones:
- Capture the why in documentation and tests
- Single sources of truth; fix unrelated failing tests
- Keep `IMPLEMENTATION_PLAN.md` current using a subagent
- Update `AGENTS.md` with operational learnings (brief)
- Document or resolve any bugs found, even if unrelated
- Implement completely — no placeholders or stubs
- Clean completed items from plan periodically
- Fix spec inconsistencies using Opus subagent with ultrathink
- Keep `AGENTS.md` operational only — progress notes go in plan

#### `AGENTS.md`

Project operational notes — the "heart of the loop." Must include:
- Build and run commands
- Validation commands (test, typecheck, lint) — this is how backpressure gets wired in
- Codebase patterns section (ralph fills this in as it learns)
- Keep brief (~60 lines). NOT a changelog or progress diary.

#### `IMPLEMENTATION_PLAN.md`

Empty file — ralph generates the content. No pre-specified template.

#### `loop.sh`

Copy from the skill's bundled `loop.sh`. This is generic and reusable across projects.

**After generating all files, present them for user review.** The prompts are the soul of the loop — always review and adjust before running.

### Phase 3 — Run the Loop

**If no plan exists:** Run planning mode first.

```bash
./loop.sh plan 5
```

Planning mode runs 1-5 iterations. Ralph reads specs, studies code, generates `IMPLEMENTATION_PLAN.md`. **Review the plan before proceeding.**

**If plan exists (or after planning):** Run building mode.

```bash
./loop.sh build
```

Each iteration:
1. **Orient** — subagents study specs and plan (up to 500 parallel reads)
2. **Read plan** — study `IMPLEMENTATION_PLAN.md`
3. **Select** — pick the most important task
4. **Investigate** — subagents study relevant source ("don't assume not implemented")
5. **Implement** — subagents for file operations
6. **Validate** — 1 subagent for build/tests (backpressure)
7. **Update plan** — mark done, note discoveries/bugs
8. **Update AGENTS.md** — if operational learnings
9. **Commit**
10. **Loop ends** — context cleared — next iteration starts fresh

Press Ctrl+C to stop, or use `./loop.sh build 30` for a max iteration count.

**When to switch back to planning mode:**
- Ralph is going off track (implementing wrong things, duplicating work)
- Plan feels stale or doesn't match current state
- Too much clutter from completed items
- Significant spec changes
- You're confused about what's actually done

The plan is disposable. Regeneration cost is one planning loop — cheap compared to ralph going in circles.

## Key Language Patterns

Use these specific phrasings in generated prompts (Huntley's tested patterns):

| Pattern | Why |
|---------|-----|
| "study" (not "read" or "look at") | Encourages deep analysis |
| "don't assume not implemented" | The Achilles' heel — ralph's biggest failure mode |
| "using parallel subagents" / "up to N subagents" | Explicit parallelism control |
| "only 1 subagent for build/tests" | Backpressure control |
| "Ultrathink" | Triggers extended reasoning for complex decisions |
| "capture the why" | Future iterations lack reasoning context |
| "keep it up to date" | Plan as shared state must be current |
| "if functionality is missing then it's your job to add it" | Prevents helplessness |
| "resolve them or document them" | Nothing gets ignored |

## Steering Ralph

You sit **on** the loop, not in it. Ralph does all the work. Your job is to engineer the setup and environment.

### Signs

When ralph misbehaves, add "signs" — the numbered lines (99999, 999999, etc.) in the prompt. But signs aren't just prompt text. They're anything ralph can discover:

- **Prompt guardrails** — explicit instructions like "don't assume not implemented"
- **`AGENTS.md`** — operational learnings about how to build/test
- **Code patterns** — when you add a utility or pattern, ralph discovers and follows it
- **Specs updates** — clarify ambiguous requirements

**Observe and course correct** — especially early on, watch what patterns emerge. Where does ralph go wrong? What signs does it need? The prompts you start with won't be the prompts you end with.

**If you need 20+ signs, the specs are probably unclear.** Fix the specs instead.

### Backpressure

Tests, typechecks, lints, builds — anything that rejects invalid work. The prompt says "run tests" generically; `AGENTS.md` specifies the actual commands. This is how backpressure gets wired in per-project.

### Model Selection

Default to **Opus** for the main loop agent. It handles task selection, prioritization, and complex reasoning better.

Consider **Sonnet** when:
- The plan is very detailed and tasks are mechanical
- You're doing simple/repetitive implementations
- Cost is a concern and specs are crystal clear

## Common Mistakes

**Skipping specs** — Ralph without specs is a random walk. The loop amplifies both good and bad inputs.

**Not reviewing generated prompts** — The prompts are the soul of the loop. Always review and adjust.

**Not reviewing the plan** — Always review `IMPLEMENTATION_PLAN.md` after planning before starting builds. Bad plans compound.

**Running on main** — Use a ralph branch (`ralph/<task-name>`). Easy to review, squash-merge, or discard.

**Expecting perfection** — Ralph is "deterministically bad in an undeterministic world." Failures are predictable. Tune the prompts based on observed failures. Never blame the model; tune the prompts.

**Bloating AGENTS.md** — Keep it operational only (~60 lines). Progress and status go in `IMPLEMENTATION_PLAN.md`.
