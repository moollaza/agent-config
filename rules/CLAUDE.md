# Operating Contract

Source: `~/projects/agent-config/rules/CLAUDE.md`. Symlinked as `~/.claude/CLAUDE.md` (Claude Code) and `~/.codex/AGENTS.md` (Codex). Topic detail in `~/.claude/rules/<topic>.md` — read on demand.

## Bad habits this contract guards against

1. **Carrying topic-shifted context across sessions.** When the user pivots, recommend `/clear` first. → `rules/context-switching.md`.
2. **Burying work in chat instead of GitHub issues.** Default to filing non-trivial follow-ups. → `rules/github-issue-habits.md`.
3. **Treating OSS repos like private ones.** Run the OSS checklist before any public commit/push/issue. → `rules/oss-repo-safety.md`.

## Non-negotiables

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
5. UI PRs: Argos green or diffs reviewed by user.

## Decision tiers

- **T1 silent**: naming, tool choice, file structure.
- **T2 log**: architecture, scope, dep additions — note in commit body.
- **T3 notify+default**: stuck >5min or wrong choice would waste >30min — state default, proceed.
- **T4 block**: destructive/irreversible, prod/shared infra, money, credentials, missing secrets.

Detail + "Consult Agents" protocol: `rules/decision-framework.md`.

## Workflow skills

Prefer skills over freeform prose for non-trivial work:

- Frame: `ce-brainstorm` (fuzzy reqs), `improve-codebase-architecture` (codebase-grounded plan).
- Plan: `ce-plan` (project plan), `to-prd` (PRD).
- Stress-test: `grill-me` / `grill-with-docs` before implementing.
- Track: `to-issues` (PRD → vertical slices), `triage` (sweep backlog).
- Build: `tdd` (testable behavior), `ce-work` (end-to-end).
- Review: `ce-review`, `argos-pr-review` (UI PRs with Argos red/pending).
- Capture: `ce-compound` (non-obvious post-fix learning).

Triggers + decision rules: `rules/workflow-skills.md`. Personal loop: `zm:plan` → `zm:research` → `zm:implement` → `zm:review` → `zm:cleanup` (+ `zm:handoff`).

## Code quality

Senior-engineer judgment. Lint and test before every commit; investigate root causes; never skip failing tests. Minimize code; reuse over rewrite. **Write helpful comments where they aid future readers** — explain non-obvious WHY, surface invariants, flag gotchas. Don't narrate what well-named code already says.

## CI/CD

Lock files (`bun.lock`, `pnpm-lock.yaml`, `package-lock.json`) required — never gitignore. Verify env-var names match deploy platform before changing CI.

## PRs, issues, debugging, communication

- PRs: `rules/pr-descriptions.md`. Use `.github/PULL_REQUEST_TEMPLATE.md` first.
- Issues: `rules/github-issue-habits.md`. Linear (in `project-hub`): `rules/linear-task-conventions.md`.
- Debugging: don't dismiss user-reported bugs; "works for me" via Playwright is not proof. → `rules/debugging.md`.
- Communication: concise, active voice, no preambles, no emoji unless asked. → `rules/communication.md`.
- Stop context: write `~/.claude/stop-context.json` before stopping (always — it's the audit record). Telegram pings only when `status: "blocked"` or `questions` is non-empty. → `rules/stop-context.md`.

## Memory + Obsidian

Auto-memory in `~/.claude/projects/<encoded-cwd>/memory/`. Read `MEMORY.md` at session start. Verify current code state before acting on memory facts. Persist cross-session insights to `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude/`. Use `skill-creator` when patterns repeat.

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
