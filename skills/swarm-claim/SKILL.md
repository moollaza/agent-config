---
name: swarm-claim
description: >
  Claim and release GitHub issues across parallel Claude Code sessions to
  prevent duplicate work, WIP swallowing, and silent overlap. Use whenever
  starting work on an issue, dispatching an agent against an issue, opening
  a PR that closes an issue, or finishing a swarm task. Triggers on "claim
  issue", "start work on issue", "release issue", "finish issue", "swarm
  claim", "in-flight", "who's working on", "is anyone working on", and any
  multi-session coordination question. Use proactively at the start of any
  task tied to a GitHub issue number — coordination is cheap, duplicate work
  is expensive. Per the operating contract (rule 11), claim before edit, and
  log to Obsidian as the source of truth.
---

# swarm-claim

Coordination protocol for running multiple Claude Code sessions against the same repo without stepping on each other. Three signals, in priority order:

1. **Obsidian `Projects/<repo>/in-flight.md`** — source of truth, verbose, persists across machines via iCloud sync. Already read at session start by [session-start.sh:54-65](../../.claude/hooks/session-start.sh).
2. **GitHub assignee** — low-noise public signal, visible to other sessions via `gh issue view`, survives session crashes, costs zero comments.
3. **Session id** — `$CLAUDE_SESSION_ID` is the tiebreaker when two sessions race on the same issue.

Public optics matter: GitHub issues on `moollaza/*` are public-facing. **Never leave claim comments on issues.** Assignee toggling + Obsidian is the entire protocol.

## Why this exists

On 2026-05-17, two parallel sessions on `choose-two` produced PR #294 and PR #287 — both fixing the same #226 regression, neither aware of the other. A separate worktree (`agent-a7ef2f8b0ba1a146d`) accumulated 6 files of UI work outside its assigned issue scope, and 5 of those 6 files shipped via sibling PRs before anyone noticed the orphan. Coordination would have caught both.

## Pre-flight check (before editing anything)

Run this before starting work on an issue. If it returns blocked, **stop and tell the user** — don't paper over the conflict.

```bash
ISSUE=$1   # e.g. 211
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO=$(basename "$REPO_ROOT")
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude"
INFLIGHT="$VAULT/Projects/$REPO/in-flight.md"

# 1. GitHub assignee check
ASSIGNEES=$(gh issue view "$ISSUE" --json assignees -q '[.assignees[].login] | join(",")')
ME=$(gh api user -q .login)
if [ -n "$ASSIGNEES" ] && ! echo "$ASSIGNEES" | grep -qw "$ME"; then
  echo "BLOCKED: issue #$ISSUE assigned to '$ASSIGNEES', not '$ME'"; exit 1
fi

# 2. Obsidian in-flight check (rows <4h old, different session)
if [ -f "$INFLIGHT" ]; then
  CUTOFF=$(date -u -v-4H +%FT%TZ)   # macOS date; on linux: date -u -d '4 hours ago' +%FT%TZ
  awk -F'|' -v iss="$ISSUE" -v cut="$CUTOFF" -v sid="${CLAUDE_SESSION_ID:-unknown}" '
    NR>2 && $2 ~ "#"iss && $4 !~ sid && $6 > cut && $7 !~ /done/ {
      print "BLOCKED: in-flight row for #"iss" session="$4" started="$6; found=1
    }
    END { exit found }
  ' "$INFLIGHT" || exit 1
fi

echo "OK: clear to claim #$ISSUE"
```

## Claim (after pre-flight passes)

Two writes — GitHub assignee and one Obsidian row. No comment, no label, no chatter.

```bash
ISSUE=$1
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO=$(basename "$REPO_ROOT")
BRANCH=$(git branch --show-current)
WORKTREE="$REPO_ROOT"
NOW=$(date -u +%FT%TZ)
SID="${CLAUDE_SESSION_ID:-unknown}"
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude"
INFLIGHT="$VAULT/Projects/$REPO/in-flight.md"

# GitHub assignee
gh issue edit "$ISSUE" --add-assignee @me

# Obsidian table — create with header if first claim for this repo
mkdir -p "$(dirname "$INFLIGHT")"
if [ ! -f "$INFLIGHT" ]; then
  cat > "$INFLIGHT" <<'EOF'
# In-flight work

Rows added when a Claude Code session claims an issue; status flipped to `done` when the corresponding PR opens. Old `done` rows are fine to leave for history.

| issue | branch | session | worktree | started | status | pr |
|-------|--------|---------|----------|---------|--------|----|
EOF
fi

printf '| #%s | %s | %s | %s | %s | in-progress |  |\n' \
  "$ISSUE" "$BRANCH" "$SID" "$WORKTREE" "$NOW" >> "$INFLIGHT"
```

## Release (on PR open or task complete)

Flip the Obsidian row to `done` and record the PR. Leave the GitHub assignee in place — it carries review continuity ("this is the human/agent on the hook to address review comments").

```bash
ISSUE=$1
PR_URL=$2   # optional but recommended
REPO=$(basename "$(git rev-parse --show-toplevel)")
SID="${CLAUDE_SESSION_ID:-unknown}"
INFLIGHT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude/Projects/$REPO/in-flight.md"
[ -f "$INFLIGHT" ] || { echo "no in-flight file for $REPO — nothing to release"; exit 0; }

# In-place edit: flip status=done and fill pr column for the row matching this issue + this session.
python3 - "$INFLIGHT" "$ISSUE" "$SID" "$PR_URL" <<'PY'
import sys, pathlib
path, issue, sid, pr = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
lines = pathlib.Path(path).read_text().splitlines()
out = []
for ln in lines:
    if ln.startswith("|") and f"#{issue}" in ln and sid in ln and "in-progress" in ln:
        parts = [p.strip() for p in ln.strip().strip("|").split("|")]
        # columns: issue, branch, session, worktree, started, status, pr
        parts[5] = "done"
        if pr:
            parts[6] = pr
        ln = "| " + " | ".join(parts) + " |"
    out.append(ln)
pathlib.Path(path).write_text("\n".join(out) + "\n")
PY
```

## Hard rules

- **No claim comments on issues.** Public optics. Assignee + Obsidian carries the full signal — anything else is noise on a public repo. The only time it's OK to comment is to *report substantive progress* (a finding, a question, a blocker) — not to mark territory.
- **Don't claim what you can't finish in this session.** If the work is exploratory and you're not sure you'll open a PR, skip the claim and document in Obsidian as a scratchpad row with `status=exploring` instead — it surfaces to other sessions but doesn't lock the issue.
- **Scope discipline.** A worktree branched for issue #N edits files in scope for #N. If you spot an adjacent bug, file a new issue, don't smuggle a fix in. Cross-scope edits are how WIP gets orphaned across parallel sessions.

## Soft norm: hotfix PRs not tied to an issue

Bug-fix PRs that don't close an issue (test repairs, regression hotfixes, CI fixes) can't claim through this skill. Before opening one, search for in-flight siblings:

```bash
gh pr list --state open --search "<keyword>" --json number,title,headRefName
```

If a sibling PR already exists, comment on theirs or coordinate with the user — don't open a duplicate. This is the lesson from PR #294 vs PR #287 on choose-two.

## When NOT to use this skill

- Solo single-session work where you know no other session is running. Coordination overhead is real; skip if there's nothing to coordinate with.
- Work not tied to a GitHub issue and not blast-radius-overlapping with other in-flight work.
- Dependabot, codex bot, or CI-bot PRs — they don't read this protocol.

## Reading the Obsidian file by hand

`Projects/<repo>/in-flight.md` is plain markdown. Open in Obsidian (synced via iCloud) or `cat` it:

```bash
REPO=$(basename "$(git rev-parse --show-toplevel)")
cat "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude/Projects/$REPO/in-flight.md"
```

The session-start hook already prints the head of this file when a session opens in a known project directory — so the next session boots with full awareness of what's in flight.

## Example invocations

- *"I'm about to start on issue 311. Anyone working on it?"* → run pre-flight, report the verdict.
- *"Claim #311 for this session"* → pre-flight + claim block.
- *"Just opened PR #340 closing #311, release the claim"* → release block with the PR URL.
- *"What's in flight on choose-two right now?"* → cat the in-flight.md file.
