---
name: sync-commands
description: Use when the user wants to sync commands from upstream, update commands from humanlayer, pull latest commands, sync upstream commands, or fix outdated commands. Triggers on phrases like "sync commands," "update commands," "pull latest from humanlayer," "sync upstream," or "commands are outdated."
---

# Sync Commands from Upstream

Sync commands from `humanlayer/humanlayer@main/.claude/commands`, applying transforms and auditing for local convention compliance.

## Process

### Step 1: Pull latest from origin

```bash
git pull origin main
```

### Step 2: Run the transform script

```bash
python3 skills/sync-commands/transform.py --apply --yes
```

The script fetches from `humanlayer/humanlayer@main/.claude/commands`, applies known transformations (rename commands, strip HL-specific content, fix directory references), and writes to `~/.claude/commands/`.

### Step 3: Check convention compliance

Run these checks to find issues the script missed:

```bash
# Check for underscore command references
grep -rn "_handoff\|_plan\|_codebase\|_fix" ~/.claude/commands/*.md

# Check for thoughts/ directory references
grep -rn "thoughts/" ~/.claude/commands/*.md

# Check for humanlayer-specific references
grep -rn "humanlayer thoughts\|hack/spec\|scripts/spec" ~/.claude/commands/*.md
```

If any issues are found, note them for fixing in Step 6.

### Step 4: Check for new upstream files

The script only syncs files listed in `COMMAND_MAPPING` and skips files in `EXCLUDED_COMMANDS`. New upstream files that aren't in either list need attention.

Review the script output for any warnings about unknown files, or compare the remote file list against both mappings in `skills/sync-commands/transform.py`.

### Step 5: Review the diff

```bash
cd ~/.claude && git diff --stat && git diff
```

**For each changed file, analyze:**

1. **What changed upstream?** Summarize key changes (new sections, removed content, modified behavior)
2. **Are there potential issues?**
   - New `/slash_command` references — do we have that command file?
   - New agent types — are they in our agents/ directory?
   - New paths or tools — do they exist in our setup?
   - Workflow assumptions that don't match our setup
3. **Are there new patterns to auto-fix?**
   - New underscore commands that should use dashes
   - New upstream command names that map to different local names
   - New directory references that need transformation

### Step 6: Fix issues

1. **Fix content issues** — Edit command files to fix convention violations or problematic references

2. **Update the transform script** — If new patterns should be auto-fixed, update `skills/sync-commands/transform.py`:
   - `apply_local_conventions()` for command name fixes
   - `transform_content()` for content transformations
   - `COMMAND_MAPPING` for new files to sync
   - `EXCLUDED_COMMANDS` for new files to skip

3. **Update this skill** — If you discover new things to watch for, update the conventions table or watch-for sections below

### Step 7: Report and commit

Present a summary:

```
## Sync Summary

### Files Updated
- file.md: [brief description of changes]

### Issues Found & Fixed
- [issue]: [how it was fixed]

### Script Updates
- [if transform script was updated, describe what was added]

### Convention Updates
- [if new conventions were discovered, list them]
```

Then commit:

```bash
git add ~/.claude/commands/*.md skills/sync-commands/transform.py skills/sync-commands/SKILL.md
git commit -m "Sync commands from humanlayer upstream

[Summary of key changes and fixes]"
```

## Local Conventions Reference

These transformations are applied automatically by the transform script:

| Upstream (humanlayer) | Local (this repo) |
|-----------------------|-------------------|
| `thoughts/` | `agent-docs/` |
| `thoughts` (standalone) | `agent-docs` |
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
2. `apply_local_conventions()` in `skills/sync-commands/transform.py`

## Things to Watch For

When auditing upstream changes:

- **New slash commands** — Do we have the command file? Add to conventions if name differs
- **New agent types** — Check agents/ directory, may need to create
- **Linear/CI references** — We don't use these, should be removed by transform
- **`humanlayer thoughts sync`** — Should be removed, we don't have this
- **`hack/` or `scripts/spec`** — HumanLayer-specific, should be removed
- **Make targets** — Verify they exist or note as TODO
- **New workflow steps** — May need adaptation for our setup

## When to Run

- Periodically to pick up upstream improvements
- After hearing about new features in humanlayer commands
- When commands feel outdated or missing functionality
- When upstream fixes bugs we also have
