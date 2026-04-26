---
name: decision-review
description: Analyze Claude's decision logs to surface patterns, anomalies, and insights. Use when the user asks "what did Claude do today", "review decisions", "what happened in my sessions", "show me the log", "any patterns", or when an agent wants to understand what tools were used, which sessions were most active, or what decisions were made. Also useful for self-improvement — identifying repeated patterns that should become skills.
---

# Decision Review

Analyze the decision logs at `~/.claude/logs/decisions-*.jsonl` to surface useful patterns.

## Step 1: Check what logs exist

```bash
ls -la ~/.claude/logs/decisions-*.jsonl 2>/dev/null | tail -10
```

If no logs exist, tell the user the decision logger hook needs to be active (`~/.claude/hooks/log-decisions.sh` via PostToolUse hook in `~/.claude/settings.json`).

## Step 2: Load and analyze

Read the relevant log file(s). Each line is JSON:

```json
{"ts":"2026-04-12T05:39:20Z","session":"abc123","tool":"Bash","input":{"command":"npm test"}}
```

## Step 3: Generate report

Produce a concise report covering:

### Session Summary
- How many sessions were active
- Which projects were worked on (infer from tool inputs — file paths, commands)
- Rough timeline (first and last timestamps per session)

### Tool Usage
- Which tools were used most (Bash, Edit, Write, Agent, etc.)
- Any unusual tool patterns (e.g. lots of Agent spawning, heavy Bash usage)

### Decision Patterns
- Commits made (look for `git commit` in Bash inputs)
- Files created or edited (Write/Edit tool inputs)
- Tests run (look for test commands)
- External calls (curl, API calls)

### Anomalies & Insights
- Sessions with very high tool counts (may indicate struggling/loops)
- Sessions that only read files (may indicate research/exploration)
- Repeated similar commands (potential automation candidates → suggest skills)

### Self-Improvement Recommendations
- Patterns that appear 3+ times → suggest creating a skill
- Common file paths → suggest adding to project knowledge
- Frequent errors in tool inputs → suggest better defaults

## Step 4: Offer next steps

Ask the user if they want to:
- Deep-dive into a specific session
- Create a skill from a repeated pattern
- Clean up old logs (anything older than 7 days)

## Log retention

Logs grow ~1-5KB per session. Suggest cleanup for files older than 30 days:

```bash
find ~/.claude/logs -name "decisions-*.jsonl" -mtime +30 -delete
```
