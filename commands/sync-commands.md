# Sync Commands from Upstream

Sync commands from humanlayer upstream, audit changes, fix issues, and update the sync infrastructure as needed.

This is the standard workflow for updating this repo with the latest commands from humanlayer.

## Process

### Step 1: Pull latest from origin

```bash
git pull origin main
```

### Step 2: Run the sync script

```bash
python3 scripts/sync-humanlayer-commands.py --apply --yes
```

The script fetches from `humanlayer/humanlayer@main/.claude/commands` and applies known transformations.

### Step 3: Check convention compliance

Run these checks to find any issues the script missed:

```bash
# Check for underscore command references
grep -rn "_handoff\|_plan\|_codebase\|_fix" commands/*.md | grep -v "sync-commands\|update-commands" | grep "^commands"

# Check for thoughts/ directory references
grep -rn "thoughts/" commands/*.md | grep -v "update-commands"

# Check for humanlayer-specific references
grep -rn "humanlayer thoughts\|hack/spec\|scripts/spec" commands/*.md
```

If any issues are found, note them for fixing.

### Step 4: Review the diff

```bash
git diff --stat
git diff
```

**For each changed file, analyze:**

1. **What changed upstream?** Summarize key changes (new sections, removed content, modified behavior)

2. **Are there potential issues?**
   - New `/slash_command` references - do we have that command file?
   - New agent types - are they in our agents/ directory?
   - New paths or tools - do they exist in our setup?
   - Workflow assumptions that don't match our setup

3. **Are there new patterns to auto-fix?**
   - New underscore commands that should use dashes
   - New upstream command names that map to different local names
   - New directory references that need transformation

### Step 5: Fix issues

1. **Fix content issues** - Edit command files to fix any convention violations or problematic references

2. **Update the sync script** - If you found new patterns that should be auto-fixed, update `scripts/sync-humanlayer-commands.py`:

   The `apply_local_conventions()` function handles command name fixes:
   ```python
   # Add new patterns here:
   content = re.sub(r'/new_command\b', '/new-command', content)
   ```

   The `transform_content()` function handles content transformations:
   ```python
   # Add new content filters here
   ```

3. **Update this command** - If you discover new things to watch for, update the "Local Conventions Reference" or "Things to Watch For" sections below

### Step 6: Report and commit

Present a summary:

```
## Sync Summary

### Files Updated
- file.md: [brief description of changes]

### Issues Found & Fixed
- [issue]: [how it was fixed]

### Script Updates
- [if sync script was updated, describe what was added]

### Convention Updates
- [if new conventions were discovered, list them]
```

Then commit:

```bash
git add commands/*.md scripts/sync-humanlayer-commands.py
git commit -m "Sync commands from humanlayer upstream

[Summary of key changes and fixes]"
```

## Local Conventions Reference

These transformations are applied automatically by the sync script:

| Upstream (humanlayer) | Local (this repo) |
|-----------------------|-------------------|
| `thoughts/` | `agent-docs/` |
| `thoughts-locator` | `agent-docs-locator` |
| `thoughts-analyzer` | `agent-docs-analyzer` |
| `/resume_handoff` | `/resume-handoff` |
| `/validate_plan` | `/validate-plan` |
| `/quick_fix` | `/quick-fix` |
| `/create_plan` | `/plan` |
| `/implementation_plan` | `/plan` |
| `/implement_plan` | `/implement` |
| `/research_codebase` | `/research` |
| `/create_handoff` | `/handoff` |

**When you find a new pattern**, add it to:
1. The table above
2. `apply_local_conventions()` in `scripts/sync-humanlayer-commands.py`

## Things to Watch For

When auditing upstream changes:

- **New slash commands** - Do we have the command file? Add to conventions if name differs
- **New agent types** - Check agents/ directory, may need to create
- **Linear/CI references** - We don't use these, should be removed by transform
- **`humanlayer thoughts sync`** - Should be removed, we don't have this
- **`hack/` or `scripts/spec`** - HumanLayer-specific, should be removed
- **Make targets** - Verify they exist or note as TODO
- **New workflow steps** - May need adaptation for our setup

## When to Run

- Periodically to pick up upstream improvements
- After hearing about new features in humanlayer commands
- When commands feel outdated or missing functionality
- When upstream fixes bugs we also have
