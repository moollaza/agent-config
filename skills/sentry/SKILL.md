---
name: sentry
description: Query and manage Sentry error tracking — search issues, analyze events, check releases, triage errors, and monitor application health. Use this skill whenever the user asks about errors, exceptions, crashes, Sentry issues, error rates, release health, debugging production errors, or application monitoring. Also trigger when the user mentions "Sentry", wants to check what's broken in production, investigate an error, review recent exceptions, or check release stability — even if they don't explicitly name Sentry.
---

# Sentry

Query error tracking data and manage issues via Sentry. This skill orchestrates the Sentry MCP tools available in the environment.

## Credential Setup

The Sentry auth token should be available as `$SENTRY_AUTH_TOKEN`. If the MCP tools are available (prefixed `mcp__claude_ai_Sentry__`), they handle authentication automatically.

If MCP tools are not available, fall back to the REST API:

```bash
SENTRY_TOKEN="${SENTRY_AUTH_TOKEN:-$(security find-generic-password -s "sentry-auth-token" -w 2>/dev/null)}"
```

If not found:

> No Sentry auth token found. Set one up:
> 1. Go to https://sentry.io/settings/auth-tokens/ (or your self-hosted instance)
> 2. Create a token with `project:read`, `event:read`, `org:read` scopes
> 3. `export SENTRY_AUTH_TOKEN=your_token`

## Using MCP Tools (Preferred)

When the Sentry MCP tools are available, prefer them over raw API calls. They handle auth, pagination, and response formatting.

### Discovery

Start by identifying the organization and project:

1. `mcp__claude_ai_Sentry__whoami` — check current auth identity
2. `mcp__claude_ai_Sentry__find_organizations` — list accessible orgs
3. `mcp__claude_ai_Sentry__find_projects` — list projects in an org

### Searching Issues

`mcp__claude_ai_Sentry__search_issues` — takes a `naturalLanguageQuery` parameter. Describe what you're looking for in plain English and the tool translates it to Sentry's search syntax internally.

Example queries (pass as naturalLanguageQuery):
- `"unresolved errors from the last 24 hours"`
- `"critical bugs affecting more than 100 users"`
- `"unresolved issues assigned to me"`
- `"new issues since last week"`
- `"errors in the quickbudget project"`
- `"unresolved and unassigned issues"`

The tool also requires `organizationSlug` and optionally `projectSlugOrId` and `regionUrl`.

### Analyzing Events

- `mcp__claude_ai_Sentry__search_events` — search events across a project
- `mcp__claude_ai_Sentry__search_issue_events` — get events for a specific issue
- `mcp__claude_ai_Sentry__get_issue_tag_values` — see tag distribution on an issue

### Issue Management

`mcp__claude_ai_Sentry__update_issue` — resolve, ignore, assign, or change priority:
- Resolve: `status: "resolved"`
- Ignore: `status: "ignored"`
- Assign: `assignedTo: "user@example.com"` or `assignedTo: "team:backend"`
- Priority: `priority: "critical"` / `"high"` / `"medium"` / `"low"`

### Releases

- `mcp__claude_ai_Sentry__find_releases` — list releases with crash-free rates
- Check release health by comparing crash-free session/user rates between releases

### AI Analysis

`mcp__claude_ai_Sentry__analyze_issue_with_seer` — use Sentry's AI to analyze an issue and get root cause suggestions.

### Supporting Tools

- `mcp__claude_ai_Sentry__get_replay_details` — session replay data
- `mcp__claude_ai_Sentry__get_profile_details` — performance profiling
- `mcp__claude_ai_Sentry__get_event_attachment` — attachments on events

## REST API Fallback

If MCP tools aren't available, use the REST API directly.

**Base URL:** `https://sentry.io/api/0/` (or your self-hosted URL)
**Auth header:** `Authorization: Bearer $SENTRY_TOKEN`

```bash
# List projects
curl -s "https://sentry.io/api/0/organizations/ORG_SLUG/projects/" \
  -H "Authorization: Bearer $SENTRY_TOKEN" | jq '.[].slug'

# Search issues
curl -s "https://sentry.io/api/0/projects/ORG_SLUG/PROJECT_SLUG/issues/?query=is:unresolved&sort=date" \
  -H "Authorization: Bearer $SENTRY_TOKEN" | jq '.[] | {id, title, culprit, count, firstSeen, lastSeen, level}'

# Get latest event for an issue
curl -s "https://sentry.io/api/0/issues/ISSUE_ID/events/latest/" \
  -H "Authorization: Bearer $SENTRY_TOKEN" | jq '{message: .message, tags: [.tags[] | {key, value}], exception: .entries[0]}'

# List releases
curl -s "https://sentry.io/api/0/organizations/ORG_SLUG/releases/?project=PROJECT_ID" \
  -H "Authorization: Bearer $SENTRY_TOKEN" | jq '.[] | {version, dateCreated, newGroups, commitCount}'
```

## Presenting Results

When showing issues, format as a table with: title, level, count, first/last seen, and assignee. For events, show the exception type, message, and relevant stack frame (file + line + function). When the user asks a vague question like "what's broken" or "any errors", show unresolved issues sorted by frequency from the last 24 hours.

### Triage Workflow

When the user wants to triage errors:

1. Search unresolved issues sorted by frequency or priority
2. For each high-priority issue, pull the latest event and show the stack trace
3. Check if the issue correlates with a recent release
4. Suggest assignment or resolution based on the stack trace context
5. If the issue is in code the user is working on, offer to look at the relevant source files

### Safety

Resolving or ignoring issues changes their state for the whole team. Confirm with the user before bulk-resolving or bulk-ignoring issues. Individual issue updates (assign, resolve) are fine to proceed with when clearly requested.
