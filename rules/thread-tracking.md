# Thread Tracking

## The forcing function

The user runs many parallel threads and easily loses track. **Linear is the source of truth for active threads. Obsidian is the source of truth for documented learning. Chat is neither — work that lives only in chat is forgotten work.**

Agents are responsible for keeping the user focused: every non-trivial thread of work must have a Linear issue (or project), opened or referenced before substantive work begins. If Linear isn't available, **stop and require setup** — don't fall back to chat-only tracking.

See `rules/linear-task-conventions.md` for issue/sub-issue title and description conventions.

## Session-start protocol (REQUIRED)

When a session begins on a known project, before substantive work:

1. **Identify the project.** Use the current repo name + `~/projects/project-hub/inventory.md` to find the matching Linear project.
2. **Query open Linear threads** scoped to that project: `mcp__linear-server__list_issues` with `project=<id>` and `state=Todo,In Progress`.
3. **Surface to the user** — one-line summary per open issue. Ask:
   > "I see N open Linear issues on `<project>`: [titles]. Are we continuing one of these, or starting new?"
4. **If new**, ask whether to file a Linear issue first. Default to yes for non-trivial work.

Skip the session-start check only when:

- Trivial single-shot tasks (typo, single-line config bump).
- The user has explicitly said "skip Linear for this session".
- Working in a repo not in the user's project list (e.g. exploring an external OSS repo).

## When Linear isn't set up — STOP

If `mcp__linear-server__*` tools fail (auth error, no team) on a project the user has stated they want tracked:

1. Halt substantive work (Tier 4).
2. Tell the user: "Linear MCP isn't reachable. I won't fall back to chat-only tracking — that's the failure mode we're guarding against. Want to (a) authenticate the Linear MCP now, (b) explicitly skip tracking for this session, or (c) work in a different repo where Linear is wired?"
3. Wait for the user's choice.

## When to open a Linear issue

Default to opening a Linear issue when **any** of these are true:

- Work is non-trivial (>30 min expected, or touches multiple files).
- A reproducible bug won't be fixed this session.
- A follow-up is identified during a PR but is out of scope.
- The user says "let's remember to..." or "follow up on..." for something not being done now.
- An adjacent issue is spotted while fixing something else.
- The user pivots to a new subject mid-session (`rules/context-switching.md`) — capture the pivot reason in the previous issue's notes, then either continue an existing related issue or open a new one.

Don't open Linear issues for: chat questions, trivial inline fixes, personal todos that don't belong on a shared backlog.

## Title format and body templates

Follow `rules/linear-task-conventions.md`:

- Title: `[Verb] [specific thing] [in/for scope]`. Verb-first.
- Parent issue body: Context / Done when / Dependencies / Notes for execution.
- Sub-issue body: Done when / Notes for execution (light — context inherited).
- Acceptance criteria must be verifiable (yes/no).

## Status hygiene during execution

- Move issue from **Todo → In Progress** when starting work.
- Move from **In Progress → Done** when acceptance criteria are met (and PR merged if applicable).
- Add a comment when blocking on something external (CI red, awaiting review, missing credential).
- Comments use Linear MCP markdown — pass real newlines, not escaped `\n`.

## When the user pivots mid-session

Per `rules/context-switching.md`: a topic switch is a thread switch. Before pivoting:

1. Update the current Linear issue with a one-line "paused at: <state>" comment.
2. If the new topic isn't a known Linear issue, ask the user whether to file one before continuing.
3. If both threads will run in parallel (the user said "keep both alive"), suggest `/clear` and a new session — context bleed across threads is exactly the failure mode we're guarding against.

## GitHub issues — secondary, OSS-contributor only

GitHub issues exist for **OSS contributor-facing work** in public repos: bug reports filed by external users, security advisories, public roadmap visibility. They are NOT the primary tracker for the user's own work.

Defaults:

- A user-reported public bug → reproduce, then mirror to a Linear issue (the work-of-record). Link the GitHub issue in Linear notes.
- A maintainer-driven feature → Linear is primary. Open a public GitHub issue only if external visibility/contribution is wanted.
- Security reports → private GitHub security advisory, not a public issue (per `rules/oss-repo-safety.md`).

When you open a GitHub issue (rare), title and body conventions still follow this rule's templates.

## Obsidian — durable learning, not active threads

Obsidian (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude/`) holds:

- **Project notes** — what the project is, decisions made, patterns that emerged.
- **Daily notes** — auto-written by the stop-event hook for journaling.
- **Templates and learnings** — patterns worth carrying across sessions.

Obsidian is **not** the active-thread tracker. Active threads belong in Linear. Use the `obsidian` skill (already installed) to write learnings post-fix; use `ce-compound` for non-obvious solutions worth team-wide capture.

## Closing the loop

When a session ends with unresolved follow-ups in chat, before stopping:

1. Group the follow-ups by Linear project.
2. Offer to file each one as a Linear issue. Ask once per project.
3. If the user declines, **note it in the current issue's comments** (not just stop-context). Chat is not durable.
