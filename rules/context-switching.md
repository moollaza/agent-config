# Context Switching

## The bad habit this guards

The user often pivots to a new subject mid-session without clearing context. Stale context bleeds into the new task: the agent recalls files from the previous topic, applies last-task heuristics to a different repo, or carries forward irrelevant TodoWrite items. Cost: wasted tokens, wrong recommendations, broken assumptions.

## When to suggest a clean session

Recommend `/clear` (Claude Code) or a fresh terminal session (Codex) when **any** of these fire:

- The user pivots to a different repo or product (e.g. was working in `autobill`, now asks about `how-many-rakats`).
- The user changes the *kind* of task (e.g. was deep in a refactor, now asks for design feedback).
- The user starts with "now let's work on..." or "ok next thing..." and the next thing is unrelated to the previous deliverable.
- Conversation has accumulated >15 unrelated tool calls and the user is starting something new.
- The user mentions a previous unfinished task and you don't have a handoff doc — better to start fresh and read the handoff than to pretend continuity.

## How to suggest it

Don't be preachy. One sentence:

> This looks like a topic shift from <previous>. Recommend `/clear` first so we don't carry old context — happy to do this in the same session if you'd rather.

Then proceed with the user's choice. If they say "stay here", drop the suggestion for the rest of the session.

## When NOT to suggest it

- Quick clarifying question on the same task.
- Continuing after a verification step (running tests, opening a browser).
- The user has explicitly disabled the prompt for this session.
- Within the first 2-3 turns of a session — there's no stale context yet.

## What to do during a clean handoff

If the user accepts a clear, before they execute `/clear`:

1. **Update the current Linear issue** with a one-line "paused at: <state>" comment via `mcp__linear-server__save_comment`. This is the durable handoff anchor — the next session resumes from this comment, not from chat memory.
2. Offer to write a handoff doc using `/zm:handoff` if there's substantial unfinished context worth preserving locally.
3. Offer to record any insights to Obsidian (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude/`) — Obsidian holds learnings, not active threads.
4. Offer to file unresolved follow-ups as Linear issues per `rules/thread-tracking.md` rather than letting them die in chat.

## Anti-patterns

- Silently carrying old TodoWrite items into a new topic.
- Pivoting to a new topic without leaving a "paused at" note on the previous Linear issue. (You will forget what state the old thread was in.)
- Recalling file paths from the previous task without re-verifying.
- Applying memory recalls about Project A while operating in Project B.
- Continuing because "it's faster" — usually it's not, since you'll re-read most of the new context anyway.
