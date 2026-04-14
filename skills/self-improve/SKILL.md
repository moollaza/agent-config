---
name: self-improve
description: Analyze decision logs for repeated patterns and propose new skills. Use this skill when the user asks to review agent behavior, find automation opportunities, analyze decision patterns, check what could be improved, or wants the agent to learn from past sessions. Also trigger when the user mentions "self-improve", "what patterns do you see", "what should be a skill", "analyze my usage", or "what am I doing repeatedly". Run this proactively at the end of a productive week.
---

# Self-Improve

Analyze decision logs to find repeated patterns and close the self-improvement loop.

## Process

### Step 1: Run the pattern analyzer

```bash
python3 skills/self-improve/scripts/analyze-patterns.py --days 7
```

For JSON output (useful for further processing):

```bash
python3 skills/self-improve/scripts/analyze-patterns.py --days 7 --json
```

Adjust `--days` based on context (use 1 for quick check, 30 for comprehensive review).
Adjust `--min-occurrences` to control sensitivity (default: 3).

### Step 2: Interpret the results

The analyzer reports:

- **Tool frequency** — which tools dominate sessions. High Bash counts may indicate missing skills.
- **Session stats** — sessions with very high tool counts (300+) may indicate thrashing or complex tasks that need decomposition.
- **Skill candidates** — two types:
  - **Tool sequences** — repeated multi-step patterns. Generic sequences (Bash -> Edit -> Bash) are normal coding; look for specific sequences involving service calls, deployments, or testing.
  - **Bash commands** — specific commands repeated 3+ times. These are the highest-signal candidates for skills or aliases.
- **Repeated Bash commands** — the most actionable signal. Look for:
  - Deploy commands (`wrangler`, `vercel`, `fly`)
  - Build/test commands (`bun run`, `npm test`, `pytest`)
  - Service queries (curl patterns to specific APIs)
  - File inspection patterns (reading the same files across sessions)

### Step 3: Propose skills

For each strong candidate:

1. Describe what the skill would do
2. Estimate frequency (how often this pattern occurs)
3. Estimate complexity (simple alias vs multi-step workflow)
4. Draft a one-paragraph skill description

Present proposals to the user. If approved, use `/skill-creator` to build each one.

### Step 4: Update Obsidian

Write a summary of findings and any created skills to the Obsidian vault:

```bash
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude"
mkdir -p "$VAULT/Projects"
```

Append to the agent-config project note with the date, findings, and actions taken.

### Step 5: Notify

If running as part of a scheduled review, send a summary via Telegram using the notify-telegram skill.

## When to Run

- Weekly review of agent behavior
- After a particularly productive or frustrating session
- When the user says "what could be better" or "analyze my patterns"
- Proactively when decision logs exceed 1,000 entries since last analysis

## What NOT to auto-create skills for

- Generic tool patterns (Bash -> Edit -> Bash is just coding)
- One-off commands that won't recur
- Commands that are already covered by existing skills
- Patterns that are better served by project-specific CLAUDE.md rules
