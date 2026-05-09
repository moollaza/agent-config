# GitHub Issue Habits

## The bad habit this guards

Non-trivial work decisions, follow-ups, and bug reports often die in chat instead of becoming trackable artifacts. Result: the user re-reports the same issue weeks later because there's no record. Issues are the cheapest, most durable place to put this.

## Default: track in issues

For any repo with a GitHub remote, default to creating an issue when **any** of these are true:

- The work is non-trivial (>30 min of expected effort, or touches multiple files).
- A bug is reproducible and won't be fixed in this session.
- A follow-up is identified during a PR but is out of scope.
- The user says "let's remember to..." or "follow up on..." or "we should fix..." for something not being done now.
- An adjacent issue is spotted while fixing something else (per `rules/CLAUDE.md` "UI Feedback: look for adjacent issues").

For Linear-tracked work in `project-hub`, follow `rules/linear-task-conventions.md` instead — that's the system of record there.

## When NOT to create an issue

- Trivial fix you're doing right now (a typo, a one-line config change).
- Question or clarification — answer in chat.
- Speculation that hasn't crystallized into an actionable thing yet.
- Personal todos that don't belong on a public/shared backlog.

## Issue title format

`[Verb] [specific thing] [in/for scope]` — same convention as `rules/linear-task-conventions.md`.

Verb-first for scannability: Add, Fix, Refactor, Remove, Update, Extract, Replace, Document, Investigate.

**Good**:
- Fix Argos build hanging on PRs from forks
- Document Cloudflare DNS setup for new projects
- Remove deprecated webhook handler

**Bad**:
- Bug
- Improvements
- Stuff that's broken

## Issue body template

```markdown
## Context
[1–3 sentences: what's happening, why it matters, where it surfaces]

## Acceptance
- [ ] [Concrete, verifiable criterion]
- [ ] [Concrete, verifiable criterion]

## Notes
[Repro steps, links, related issues/PRs, files to check]
```

Acceptance criteria must be verifiable (yes/no). "Works properly" is not acceptance.

## Public-repo issues

If the repo is public (per `rules/oss-repo-safety.md`):

- Strip private context from the title and body. No internal URLs without `(internal)` marker.
- No personal email/phone/account IDs.
- For security-sensitive issues, use a private advisory, **not** a public issue.
- Use neutral, factual voice. Reviewers may be strangers.

## Linking to PRs

- PRs that close issues should reference them with `Closes #N` or `Fixes #N` in the description, so GitHub auto-closes on merge.
- If a PR partially addresses an issue, use `Refs #N` and update the issue with what's still outstanding.

## Labels

If the repo uses labels, default to:

- **Type**: `bug`, `feature`, `chore`, `refactor`, `docs`.
- **Scope** (if multi-area repo): `frontend`, `backend`, `infra`, `ci`.
- **Priority** (only if the user asks or the bug is severe): `priority:high`.

Don't invent new label taxonomies — match what the repo already uses (`gh label list`).

## When to suggest creating an issue (vs just doing it)

Always offer; don't surprise-create. Pattern:

> Want me to file this as an issue in `<repo>`? Title would be "<title>", marking it [bug/chore/etc].

If the user says yes, run `gh issue create --title ... --body ...` with the templated body. Confirm the issue URL after creation.

## Closing the loop

When a session ends with unresolved follow-ups in chat, before stopping:

1. Group the follow-ups by repo.
2. Offer to file each one. Don't batch — ask once per repo.
3. If the user declines, note the follow-ups in the stop-context message so they're not lost.
