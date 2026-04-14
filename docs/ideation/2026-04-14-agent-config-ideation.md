---
date: 2026-04-14
topic: agent-config-improvements
focus: open-ended
---

# Ideation: Agent Config Improvements

## Codebase Context
- Config repo for Claude Code: 9 skills, 9 agents, 9 commands, 3 hooks
- 4 service integrations just built and tested (Fathom, GSC, Cloudflare, Sentry)
- Telegram notifications working via stop hook
- Decision logs capture all tool use to JSONL
- Obsidian vault referenced but barely populated
- Linear MCP available, task conventions written
- Agent teams experimental feature enabled

## Ranked Ideas

### 1. Morning Briefing via CronCreate
**Description:** Daily autonomous loop querying all 4 service integrations and pushing a consolidated briefing to Telegram. Sentry errors overnight, Fathom traffic anomalies, Cloudflare security events, Linear tasks due today.
**Rationale:** All plumbing exists. Transforms agent from reactive to proactive. Highest-leverage for a solo dev shipping 7 apps.
**Downsides:** CronCreate is experimental. Briefing quality depends on good thresholds. Costs tokens on quiet days.
**Confidence:** 80%
**Complexity:** Medium
**Status:** Unexplored

### 2. Service Registry (Project Switchboard)
**Description:** A `~/.claude/service-registry.json` mapping each project to its service identifiers (Cloudflare zone ID, Fathom site ID, Sentry project slug, GSC property URL). Skills auto-resolve without discovery API calls.
**Rationale:** Every service skill repeats a discovery step every session. Eliminates wasted API calls and context tokens. Foundation for cross-service workflows.
**Downsides:** Another config file to maintain.
**Confidence:** 90%
**Complexity:** Low
**Status:** Selected for implementation

### 3. Self-Improve Skill (decision logs -> skill creation)
**Description:** Analyzes decision logs, identifies repeated multi-step tool sequences (3+ occurrences), auto-drafts new skills via skill-creator. Closes the logging-to-capability loop.
**Rationale:** Explicitly planned in Obsidian design doc. Decision logs have 1,700+ entries. Decision-review skill identifies patterns but stops at suggestions.
**Downsides:** Pattern detection quality is hard. Needs human approval gate.
**Confidence:** 65%
**Complexity:** High
**Status:** Selected for implementation

### 4. Linear-Driven Autonomous Work Queue
**Description:** Polls Linear for "Todo" issues, executes via zm:implement pipeline, marks "Done" on completion. User queues work; Claude drains it.
**Rationale:** Linear MCP configured, task conventions written, zm:* commands provide execution lifecycle.
**Downsides:** Bold. Needs guardrails (PR-only, no direct push).
**Confidence:** 55%
**Complexity:** High
**Status:** Deferred to ce:brainstorm/plan/work cycle

### 5. Eliminate stop-context.json
**Description:** Stop hook auto-synthesizes notification context from decision logs, git status, and branch name instead of requiring manual JSON authoring.
**Rationale:** Silent failure mode when Claude forgets to write the file. Weakest link in notification system.
**Downsides:** Hook may not have direct access to conversation state.
**Confidence:** 75%
**Complexity:** Medium
**Status:** Selected for implementation

### 6. Session Context Auto-Loading via Obsidian
**Description:** Hook that reads relevant Obsidian project note at session start and auto-appends structured summary at session end.
**Rationale:** CLAUDE.md says "check Obsidian at start" but nothing enforces it. Automating both read and write sides makes cross-session memory real.
**Downsides:** Obsidian on iCloud may have sync latency. Auto-notes could be noisy.
**Confidence:** 70%
**Complexity:** Medium
**Status:** Selected for implementation

### 7. Bing Webmaster API Integration
**Description:** Add Bing Webmaster Tools as a 5th service integration skill, similar to GSC.
**Rationale:** User cares about search visibility. Bing has a simpler API key auth (no OAuth dance). Complements GSC.
**Downsides:** Lower traffic share than Google for most sites.
**Confidence:** 85%
**Complexity:** Low
**Status:** Unexplored

## Rejection Summary

| # | Idea | Reason Rejected |
|---|------|-----------------|
| 1 | Nix Flake for setup | Overkill for single-user repo |
| 2 | Collapse 4 service skills to 1 | Premature abstraction |
| 3 | Hook Composition Language | Over-engineering for 3 shell scripts |
| 4 | Hook Testing Harness | Low leverage compared to alternatives |
| 5 | Credential Vending Machine | Can't automate external service UIs |
| 6 | Auto-Sync Upstream Commands via cron | Minor quality-of-life |
| 7 | Git hook for symlink sync | Trivially low impact |
| 8 | Skill Dependency Graph | Premature with only 9 skills |
| 9 | Agent Team Playbooks | Too speculative |
| 10 | Mid-session notification enrichment | Low urgency, adds noise |
| 11 | Cross-Session Memory Graph (SQLite) | Over-engineering |
| 12 | Skill Effectiveness Telemetry | Needs self-improve pipeline first |
| 13 | Self-Modifying Operating Contract | High risk of config drift |
| 14 | Parallel Track on Block | Too complex for current maturity |
| 15 | Session Replay from Decision Logs | Read-only, lower leverage |
| 16 | Composable Skill Pipelines (YAML) | Morning Briefing achieves this concretely |
| 17 | Credential Health Monitor | Subsumed by Morning Briefing |
| 18 | Portable Agent Config | Single user, single machine |

## Session Log
- 2026-04-14: Initial ideation -- 40 candidates generated across 5 frames, 7 survived filtering. Items 2, 3, 5, 6 selected for immediate implementation. Item 4 deferred to ce:brainstorm cycle.
