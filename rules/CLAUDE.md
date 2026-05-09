# Operating Contract

Source: `~/projects/agent-config/rules/CLAUDE.md`. Symlinked as `~/.claude/CLAUDE.md` (Claude Code) and `~/.codex/AGENTS.md` (Codex). Topic detail in `~/.claude/rules/<topic>.md` — read on demand.

## Forcing function: Linear is the source of truth for active threads

The user runs many parallel threads and easily loses track. **Active threads live in Linear. Documented learning lives in Obsidian. Chat is neither.** Agents are responsible for keeping the user focused — every non-trivial thread of work must have a Linear issue opened or referenced before substantive work begins.

**Session-start protocol** (skip only for trivial single-shot tasks):

1. Identify the current project (repo name + `~/projects/project-hub/inventory.md`).
2. Query open Linear threads for that project via `mcp__linear-server__list_issues`.
3. Surface to the user — "I see N open threads on `<project>`: [titles]. Continuing one, or new?"
4. New thread → ask whether to file a Linear issue first. Default to yes for non-trivial work.

**If Linear MCP fails or isn't wired** for a project the user wants tracked: **STOP** (Tier 4). Do not fall back to chat-only tracking — that's the failure mode this rule guards against. Detail and triggers: `rules/thread-tracking.md`.

## Bad habits this contract guards against

1. **Working without a Linear thread of record.** Linear-first; see above + `rules/thread-tracking.md`.
2. **Carrying topic-shifted context across sessions.** When the user pivots, update the current Linear thread, then recommend `/clear`. → `rules/context-switching.md`.
3. **Treating OSS repos like private ones.** Run the OSS checklist before any public commit/push/issue. → `rules/oss-repo-safety.md`.

## Non-negotiables

- **Linear thread or stop.** Non-trivial work has a Linear issue before substantive code lands. If MCP is unreachable, halt and ask the user to authenticate or explicitly skip.
- Keep going until **Definition of Done** is met. Don't ask "should I continue?"
- If blocked, try yourself first. If stuck, ask **one** question with **2–3 options** + recommended default.
- **No silent deletions.** Only delete what you created in this PR, were told to delete, or got explicit confirmation for. Enumerate every deletion in the PR description.
- **Public artifacts are permanent.** No personal email/phone/address/account-IDs, no private dashboard URLs, no tokens or secrets. Use placeholders, aliases, env vars.
- **Bounded loops only.** Every script/automated loop has an exit condition + max iteration cap.

## Definition of Done

1. Requirements implemented (as stated + accepted clarifications).
2. Lint and tests pass — run before every commit.
3. No new TODO/FIXME related to this work.
4. Docs updated if behavior, APIs, or setup changed.
5. **Linear issue moved to Done** (or appropriate state) and PR linked in issue notes.
6. UI PRs: Argos green or diffs reviewed by user.

## Decision tiers

- **T1 silent**: naming, tool choice, file structure.
- **T2 log**: architecture, scope, dep additions — note in commit body and Linear issue.
- **T3 notify+default**: stuck >5min or wrong choice would waste >30min — state default, proceed.
- **T4 block**: destructive/irreversible, prod/shared infra, money, credentials, missing secrets, **missing Linear context**.

Detail + "Consult Agents" protocol: `rules/decision-framework.md`.

## Workflow skills

Prefer skills over freeform prose for non-trivial work:

- Frame: `ce-brainstorm` (fuzzy reqs), `improve-codebase-architecture` (codebase-grounded plan).
- Plan: `ce-plan` (project plan), `to-prd` (PRD → publishes to Linear via the Agent Skills config below).
- Stress-test: `grill-me` / `grill-with-docs` before implementing.
- Track: `to-issues` (PRD → vertical slices in Linear), `triage` (sweep Linear backlog).
- Build: `tdd` (testable behavior), `ce-work` (end-to-end).
- Review: `ce-review`, `argos-pr-review` (UI PRs with Argos red/pending).
- Capture: `ce-compound` (non-obvious post-fix learning) → also write to Obsidian.

Triggers + decision rules: `rules/workflow-skills.md`. Personal loop: `zm:plan` → `zm:research` → `zm:implement` → `zm:review` → `zm:cleanup` (+ `zm:handoff`).

## Agent Skills config (Matt Pocock skills → Linear MCP)

Matt's `to-prd`, `to-issues`, `triage`, `tdd`, `improve-codebase-architecture`, and `zoom-out` skills all expect "an issue tracker" to be configured here. **Override the upstream `setup-matt-pocock-skills` defaults — use Linear, not GitHub.**

- **Tracker**: Linear, via `mcp__linear-server__*` tools (NOT GitHub).
- **Default team**: "Side Projects" (key `ZPR`). Pick the project whose name matches the current repo from `mcp__linear-server__list_projects`. If no match, ask the user before creating issues in a different project.
- **Create issue**: `mcp__linear-server__save_issue` with `team`, `project`, `title`, `description`, `labels`. Pass real newlines in markdown — never escaped `\n`.
- **List/search**: `mcp__linear-server__list_issues` with `project`, `state`, `assignee`.
- **Update**: pass the issue `id` to `mcp__linear-server__save_issue`.
- **Comments**: `mcp__linear-server__save_comment` with the issue id.

Canonical triage labels → Linear labels (create them on first use if missing):

- `bug` → `bug`
- `enhancement` → `enhancement`
- `needs-triage` → `triage:needs-triage`
- `needs-info` → `triage:needs-info`
- `ready-for-agent` → `triage:ready-for-agent`
- `ready-for-human` → `triage:ready-for-human`
- `wontfix` → `triage:wontfix`

Domain glossary: `CONTEXT.md` at repo root (if present). ADRs: `docs/adr/`. Issue/sub-issue conventions: `rules/linear-task-conventions.md`.

## Code quality

Senior-engineer judgment. Lint and test before every commit; investigate root causes; never skip failing tests. Minimize code; reuse over rewrite. **Write helpful comments where they aid future readers** — explain non-obvious WHY, surface invariants, flag gotchas. Don't narrate what well-named code already says.

## CI/CD

Lock files (`bun.lock`, `pnpm-lock.yaml`, `package-lock.json`) required — never gitignore. Verify env-var names match deploy platform before changing CI.

## PRs, issues, debugging, communication

- PRs: `rules/pr-descriptions.md`. Use `.github/PULL_REQUEST_TEMPLATE.md` first. Reference the Linear issue id in the body.
- Threads: `rules/thread-tracking.md` (Linear primary). Linear conventions: `rules/linear-task-conventions.md`. GitHub issues are OSS-contributor-facing only.
- Debugging: don't dismiss user-reported bugs; "works for me" via Playwright is not proof. → `rules/debugging.md`.
- Communication: concise, active voice, no preambles, no emoji unless asked. → `rules/communication.md`.
- Stop context: write `~/.claude/stop-context.json` before stopping (always — it's the audit record). Telegram pings only when `status: "blocked"` or `questions` is non-empty. → `rules/stop-context.md`.

## Memory + Obsidian (durable learning)

- Auto-memory in `~/.claude/projects/<encoded-cwd>/memory/`. Read `MEMORY.md` at session start. Verify current code state before acting on memory facts.
- Obsidian (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude/`) is the **documented-learning** store — project notes, daily journal, decisions, patterns. **Not** the active-thread tracker (that's Linear). Use the `obsidian` skill to write learnings; use `ce-compound` for non-obvious post-fix capture.
- Use `skill-creator` when patterns repeat.

## Maintaining

Edit `~/projects/agent-config/`, then `python3 sync-to-ides.py` to refresh symlinks for both Claude Code and Codex. External skills live in `plugins.json`.

<!-- BEGIN COMPOUND CODEX TOOL MAP -->
## Compound Codex Tool Mapping (Claude Compatibility)

This section maps Claude Code plugin tool references to Codex behavior. Auto-managed.

- Read: `cat`/`sed` or `rg`
- Write: shell redirection or `apply_patch`
- Edit/MultiEdit: `apply_patch`
- Bash: `shell_command`
- Grep: `rg` (fallback: `grep`)
- Glob: `rg --files` or `find`
- LS: `ls` via `shell_command`
- WebFetch/WebSearch: `curl` or Context7
- AskUserQuestion: numbered list, wait for reply. Multi-select = comma-separated.
- Task/Subagent/Parallel: sequential in main thread; `multi_tool_use.parallel` for tool calls.
- TodoWrite/TodoRead: file-based todos in `todos/`.
- Skill: open referenced `SKILL.md`.
- ExitPlanMode: ignore.
<!-- END COMPOUND CODEX TOOL MAP -->
