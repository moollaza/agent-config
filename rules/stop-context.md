# Stop Context

Before stopping for **any** reason, write `~/.claude/stop-context.json`. The notification hook reads it to journal the stop locally (Obsidian daily note) and to decide whether to ping the user via Telegram.

**Telegram fires only when `status == "blocked"` or `questions` is non-empty** — done-pings were too noisy. Always write the file anyway: it's the audit record and forces you to summarize state before stopping.

## Schema

```json
{
  "conversation": "short-name (e.g. 'auth-refactor', 'fix-upload-bug')",
  "task": "what you were working on",
  "progress": "- Done: X\n- Done: Y\n- Remaining: Z",
  "reason": "why you stopped — be specific",
  "status": "done | blocked",
  "questions": "questions for the user, only if blocked; else empty string"
}
```

## Field guidance

- **`conversation`**: short, branch-name-like (`auth-refactor`, not `Working on auth`). This is the heading the user sees.
- **`task`**: one sentence describing the deliverable, not the action verb.
- **`progress`**: bullet list of what's done, what's remaining. Concrete, not vague.
- **`reason`**: why you stopped. "Done" is fine when truly done; otherwise be specific ("Argos has unreviewed diffs", "missing GH_TOKEN", "user reviewed plan, awaiting choice").
- **`status`**: `"done"` when DoD is satisfied; `"blocked"` when waiting on user/external.
- **`questions`**: only populate when blocked. Phrase to be answerable from a phone — short, with 2-3 options if possible.

## Stop conditions (only these allow stopping)

- A required secret/credential is missing AND cannot be stubbed/mocked.
- A required external system is down.
- You hit a hard limit (context/time/tooling).
- A Tier 4 decision requires user input (per `rules/decision-framework.md`).
- The task is fully done — DoD met (per root CLAUDE.md).

If stopping due to a blocker, also output in the terminal:

- Current state.
- Exact next steps (commands + files).
- Minimal context to resume.

## Examples

### Done

```json
{
  "conversation": "argos-rules-cleanup",
  "task": "Move Argos PR review guidance from CLAUDE.md to its own rule file",
  "progress": "- Done: created rules/argos-pr-review.md\n- Done: trimmed CLAUDE.md\n- Done: synced and verified symlinks",
  "reason": "Done",
  "status": "done",
  "questions": ""
}
```

### Blocked

```json
{
  "conversation": "argos-rules-cleanup",
  "task": "Move Argos PR review guidance from CLAUDE.md to its own rule file",
  "progress": "- Done: drafted rules/argos-pr-review.md\n- Remaining: confirm preferred filename: 'argos.md' vs 'argos-pr-review.md'",
  "reason": "Tier 3 naming question with two reasonable options",
  "status": "blocked",
  "questions": "Filename: (a) argos-pr-review.md (matches skill name) or (b) argos.md (terser)? Default (a)."
}
```
