# Sync Commands from Upstream

Sync commands from humanlayer upstream, audit changes, and ensure local convention compliance.

## Process

### Step 1: Pull latest from origin
```bash
git pull origin main
```

### Step 2: Run the sync script
```bash
python3 scripts/sync-humanlayer-commands.py --apply --yes
```

The script automatically applies known transformations (command names, directory references).

### Step 3: Audit the changes

After syncing, carefully review what changed:

```bash
git diff --stat
git diff
```

**For each changed file, analyze:**

1. **What changed upstream?** - Summarize the key changes (new sections, removed content, modified behavior)

2. **Are there potential issues?** Look for:
   - New command references that might not exist locally
   - New agent names or subagent types we don't have
   - References to humanlayer-specific tools, scripts, or paths
   - Workflow changes that might not fit our setup
   - New dependencies or integrations

3. **Convention compliance** - Verify no issues slipped through:
   ```bash
   grep -n "resume_handoff\|validate_plan\|create_plan\|implement_plan\|research_codebase\|create_handoff" commands/*.md | grep -v "sync-commands\|update-commands"
   grep -n "thoughts/" commands/*.md | grep -v update-commands.md
   ```

### Step 4: Report findings

Present a summary to the user:

```
## Sync Summary

### Files Updated
- [list files and brief description of changes]

### Potential Issues Found
- [issue 1]: [description and suggested fix]
- [issue 2]: [description and suggested fix]

### Recommended Actions
1. [action to take]
2. [action to take]
```

### Step 5: Fix issues and commit

1. Fix any issues identified in the audit
2. Commit the changes:
   ```bash
   git add commands/*.md
   git commit -m "Sync commands from humanlayer upstream

   [Brief description of key changes]"
   ```

## Local Conventions Reference

| Upstream (humanlayer) | Local (this repo) |
|-----------------------|-------------------|
| `thoughts/` | `agent-docs/` |
| `thoughts-locator` | `agent-docs-locator` |
| `thoughts-analyzer` | `agent-docs-analyzer` |
| `/resume_handoff` | `/resume-handoff` |
| `/validate_plan` | `/validate-plan` |
| `/create_plan` | `/plan` |
| `/implementation_plan` | `/plan` |
| `/implement_plan` | `/implement` |
| `/research_codebase` | `/research` |
| `/create_handoff` | `/handoff` |

## Things to Watch For

When auditing upstream changes, pay special attention to:

- **New slash commands** - Do we have the corresponding command file?
- **New agent types** - Are they defined in our agents/ directory?
- **Linear/CI references** - We don't use these, should be removed
- **Absolute paths** - Should use relative or configurable paths
- **Make targets** - Verify they exist or adapt to our setup
- **Sync commands** - References to `humanlayer thoughts sync` should be removed

## When to Run

- Periodically to pick up upstream improvements
- After hearing about new features in humanlayer commands
- When commands feel outdated or missing functionality
