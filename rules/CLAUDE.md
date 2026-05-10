# Operating Contract

Source: `~/projects/agent-config/rules/CLAUDE.md` → `~/.claude/CLAUDE.md`. Codex parallel: `rules/AGENTS.md`. Topic detail in `~/.claude/rules/<topic>.md` — read on demand.

## Two forcing functions

These are the habits the user loses without. Everything else is guidelines.

**Linear = active threads. Obsidian = documented learning. Chat is neither.** Before non-trivial work, check open Linear threads on the current project (`mcp__linear-server__list_issues`; repo → project mapping in `~/projects/project-hub/inventory.md`). New thread? Default to filing one first. If Linear MCP isn't reachable on a tracked project, halt — don't fall back to chat. Detail: `rules/thread-tracking.md`.

**Default to skills, not freeform prose.** Canonical chain: plan (`ce-plan` / `to-prd`) → deepen (`deepen-plan`) → stress-test (`grill-me` / `grill-with-docs`) → track (`to-issues` / `triage`) → build (`tdd` / `ce-work`) → review (`ce-review` / `argos-pr-review`) → capture (`ce-compound` + Obsidian). Personal `zm:*` chain is equally valid. Unsure which? `find-skills`. Detail: `rules/workflow-skills.md`.

## Non-negotiables

- Keep going until DoD is met. Don't ask "should I continue?"
- If stuck, ask one question with 2–3 options + recommended default.
- **No silent deletions.** Only delete what you created in this PR, were told to delete, or got explicit OK on. Enumerate deletions in the PR body.
- **Public artifacts are permanent.** No personal email/phone/address/IDs, private dashboard URLs, tokens or secrets in any artifact. → `rules/oss-repo-safety.md`.
- **Topic switches preserve threads.** On a pivot, leave a "paused at" comment on the current Linear issue, then `/clear`. → `rules/context-switching.md`.
- **Bounded loops only.** Exit condition + iteration cap, always.

## Definition of Done

Requirements met. Lint and tests pass. No new TODO/FIXME related to this work. Docs updated if behavior/API/setup changed. Linear issue moved to Done (or appropriate state) with the PR linked in notes.

## Decision tiers

- **T1 silent**: naming, structure, tool choice.
- **T2 log**: architecture, scope, dep additions — note in commit body and Linear.
- **T3 notify + default**: stuck >5min or wrong choice would waste >30min — state default and proceed.
- **T4 block**: destructive/irreversible, prod/shared infra, money, credentials, missing secrets, **missing Linear context**.

Detail: `rules/decision-framework.md`.

## Agent Skills config (Matt Pocock skills → Linear MCP)

Matt's `to-prd`, `to-issues`, `triage`, `tdd`, `improve-codebase-architecture`, and `zoom-out` look here for tracker config. **Use Linear, not GitHub.**

- Tracker: Linear via `mcp__linear-server__*`.
- Default team: "Side Projects" (key `ZPR`). Pick the project whose name matches the current repo from `mcp__linear-server__list_projects`.
- Create / list / update issues: `save_issue` / `list_issues` / `save_issue` (with `id`). Comment: `save_comment`. Pass real newlines in markdown — never escaped `\n`.

Triage label mapping (canonical → Linear):

- Category (already in team): `bug` → `Bug`, `enhancement` → `Feature` (or `Improvement`), chore-class → `Chore`.
- Triage state (workspace, already created): `triage:needs-triage` / `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`.

Domain glossary: `CONTEXT.md`. ADRs: `docs/adr/`. Issue conventions: `rules/linear-task-conventions.md`.

## Code quality

Senior-engineer judgment. Lint and test before every commit. Investigate root causes; never skip failing tests. Minimize code; reuse over rewrite. Write helpful comments where they aid future readers (non-obvious WHY, invariants, gotchas) — don't narrate what well-named code says.

## Pointers

- **PRs**: `rules/pr-descriptions.md`. Use `.github/PULL_REQUEST_TEMPLATE.md` first. Reference the Linear issue id.
- **Debugging**: don't dismiss user-reported bugs; "works for me" via Playwright is not proof. → `rules/debugging.md`.
- **Communication**: concise, active voice, no preambles, no emoji unless asked. → `rules/communication.md`.
- **Stop context**: write `~/.claude/stop-context.json` before stopping (audit record). Telegram only when `status: "blocked"` or `questions` non-empty. → `rules/stop-context.md`.
- **CI/CD**: lock files (`bun.lock` / `pnpm-lock.yaml` / `package-lock.json`) required — never gitignore. Verify env-var names match deploy platform before changing CI.

## Memory + Obsidian

Auto-memory at `~/.claude/projects/<encoded-cwd>/memory/`. Read `MEMORY.md` at session start; verify current code state before acting on memory facts. Persist learnings to Obsidian (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude/`) — not active threads, those are Linear. Use `skill-creator` when patterns repeat.

## Maintaining

Edit `~/projects/agent-config/`, then `python3 sync-to-ides.py`. External skills in `plugins.json`.
