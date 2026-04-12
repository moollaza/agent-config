# Sync Commands Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the sync-commands workflow from a command + script pair into a single bundled skill with deterministic transforms and intelligent auditing.

**Architecture:** Option C hybrid — a skill directory containing `SKILL.md` (orchestration + audit logic) and `transform.py` (deterministic fetch/transform/write). The skill replaces both `commands/sync-commands.md` and `commands/update-commands.md`. References in `rules/CLAUDE.md` and `README.md` are updated.

**Tech Stack:** Python 3 (transform script), Markdown (skill definition)

---

## File Structure

```
skills/sync-commands/
  SKILL.md              # Skill definition with orchestration + audit logic
  transform.py          # Deterministic fetch/transform/write (moved from scripts/)
```

**Files to remove:**
- `commands/sync-commands.md` — replaced by `skills/sync-commands/SKILL.md`
- `commands/update-commands.md` — older manual version, fully superseded
- `scripts/sync-humanlayer-commands.py` — moved to `skills/sync-commands/transform.py`

**Files to modify:**
- `rules/CLAUDE.md:26` — update `/sync-commands` reference
- `README.md:82-96` — update sync section (script path + command reference)
- `docs/FORMATS.md:22` — update stale `sync-humanlayer-commands.py` reference

---

### Task 1: Create the skill directory and move the transform script

**Files:**
- Create: `skills/sync-commands/SKILL.md`
- Move: `scripts/sync-humanlayer-commands.py` → `skills/sync-commands/transform.py`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p skills/sync-commands
```

- [ ] **Step 2: Move the Python script**

```bash
git mv scripts/sync-humanlayer-commands.py skills/sync-commands/transform.py
```

- [ ] **Step 3: Update the script's commands-dir default**

The script currently defaults to `~/.claude/commands`. It should keep this default since it writes to the user's commands directory, not the repo. Verify:

```bash
grep -- '--commands-dir' skills/sync-commands/transform.py
```

Expected: `default='~/.claude/commands'` — no change needed.

- [ ] **Step 4: Commit the move**

```bash
git add skills/sync-commands/transform.py
git commit -m "Move sync script to skills/sync-commands/transform.py"
```

---

### Task 2: Write the SKILL.md

**Files:**
- Create: `skills/sync-commands/SKILL.md`

The skill combines the orchestration from `commands/sync-commands.md` with the documentation from `commands/update-commands.md` into a single skill definition. Key design decisions:

- Frontmatter matches ralph-loop pattern (`name`, `description`)
- Script is referenced by relative path `transform.py`
- The audit/fix/update-script logic lives in the skill markdown (Claude does this part)
- Convention reference table is preserved for auditability

- [ ] **Step 1: Write SKILL.md with frontmatter and full content**

Write `skills/sync-commands/SKILL.md` with this content:

```markdown
---
name: sync-commands
description: Use when the user wants to sync, update, or pull the latest commands from humanlayer upstream. Also use when the user mentions "sync commands," "update commands," "pull latest from humanlayer," "sync upstream," or when commands feel outdated. This skill fetches, transforms, audits, and applies upstream command changes with local convention enforcement.
---

# Sync Commands from Upstream

Sync commands from humanlayer upstream, audit changes, fix issues, and update the sync infrastructure as needed.

## Process

### Step 1: Pull latest from origin

` ` `bash
git pull origin main
` ` `

### Step 2: Run the transform script

The skill bundles `transform.py` — a deterministic script that fetches from `humanlayer/humanlayer@main/.claude/commands`, applies known transformations, and writes to the commands directory.

` ` `bash
python3 skills/sync-commands/transform.py --apply --yes
` ` `

### Step 3: Check convention compliance

Run these checks to find any issues the script missed:

` ` `bash
# Check for underscore command references
grep -rn "_handoff\|_plan\|_codebase\|_fix" commands/*.md | grep -v "sync-commands\|update-commands" | grep "^commands"

# Check for thoughts/ directory references
grep -rn "thoughts/" commands/*.md | grep -v "update-commands"

# Check for standalone "thoughts" references (without trailing slash)
grep -rn "\bthoughts\b" commands/*.md | grep -v "update-commands\|agent-docs"

# Check for humanlayer-specific references
grep -rn "humanlayer thoughts\|hack/spec\|scripts/spec" commands/*.md
` ` `

If any issues are found, note them for fixing.

### Step 4: Check for new upstream files

` ` `bash
# Compare upstream file list against our mapping + exclusion lists in transform.py
# Look for files not in COMMAND_MAPPING or EXCLUDED_COMMANDS
` ` `

For any new upstream files found:
- Evaluate if they would be useful for our workflow
- If useful: add to `COMMAND_MAPPING` in `transform.py` and re-run
- If not useful: add to `EXCLUDED_COMMANDS` in `transform.py`

### Step 5: Review the diff

` ` `bash
git diff --stat
git diff
` ` `

**For each changed file, analyze:**

1. **What changed upstream?** Summarize key changes
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

1. **Fix content issues** — Edit command files to fix any convention violations or problematic references

2. **Update the transform script** — If you found new patterns that should be auto-fixed, update `skills/sync-commands/transform.py`:

   The `apply_local_conventions()` function handles command name fixes:
   ` ` `python
   # Add new patterns here:
   content = re.sub(r'/new_command\b', '/new-command', content)
   ` ` `

   The `transform_content()` function handles content transformations.

3. **Update this skill** — If you discover new things to watch for, update the "Local Conventions Reference" or "Things to Watch For" sections below

### Step 7: Report and commit

Present a summary:

` ` `
## Sync Summary

### Files Updated
- file.md: [brief description of changes]

### Issues Found & Fixed
- [issue]: [how it was fixed]

### Script Updates
- [if transform.py was updated, describe what was added]

### Convention Updates
- [if new conventions were discovered, list them]
` ` `

Then commit:

` ` `bash
git add commands/*.md skills/sync-commands/transform.py skills/sync-commands/SKILL.md
git commit -m "Sync commands from humanlayer upstream

[Summary of key changes and fixes]"
` ` `

## Local Conventions Reference

These transformations are applied automatically by `transform.py`:

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
2. `apply_local_conventions()` in `transform.py`

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
```

Note: Replace `` ` ` ` `` with actual triple backticks in the real file.

- [ ] **Step 2: Verify the skill has correct frontmatter**

```bash
head -4 skills/sync-commands/SKILL.md
```

Expected: frontmatter with `name: sync-commands` and a description.

- [ ] **Step 3: Commit the skill**

```bash
git add skills/sync-commands/SKILL.md
git commit -m "Add sync-commands skill definition"
```

---

### Task 3: Remove old commands and update references

**Files:**
- Delete: `commands/sync-commands.md`
- Delete: `commands/update-commands.md`
- Modify: `rules/CLAUDE.md:26`
- Modify: `README.md:82-96`
- Modify: `docs/FORMATS.md:22`

- [ ] **Step 1: Remove the old command files**

```bash
git rm commands/sync-commands.md commands/update-commands.md
```

- [ ] **Step 2: Update rules/CLAUDE.md reference**

Change line 26 from:
```
- **Sync commands from upstream** - Use `/sync-commands` to pull latest from humanlayer and audit changes
```
To:
```
- **Sync commands from upstream** - Use the `sync-commands` skill to pull latest from humanlayer and audit changes
```

- [ ] **Step 3: Update README.md sync section (lines 82-96)**

Replace the entire "Syncing Commands from Upstream" section:

From:
```markdown
## Syncing Commands from Upstream

Commands are synced from `humanlayer/humanlayer@main/.claude/commands`. To update:

\```bash
# Pull latest and run sync
git pull origin main
python3 scripts/sync-humanlayer-commands.py --apply --yes
\```

After syncing, audit for local convention compliance:
- Command names use dashes: `/resume-handoff` not `/resume_handoff`
- Directory references use `agent-docs/` not `thoughts/`

See `/sync-commands` for the full process.
```

To:
```markdown
## Syncing Commands from Upstream

Commands are synced from `humanlayer/humanlayer@main/.claude/commands`. Use the `sync-commands` skill which runs the bundled transform script and audits for convention compliance.
```

- [ ] **Step 4: Update docs/FORMATS.md reference**

Change line 22 from:
```
└── sync-humanlayer-commands.py  # Utility scripts
```
To:
```
├── skills/                # Bundled skills with assets
│   ├── sync-commands/     # Upstream command sync
│   └── ralph-loop/        # Autonomous dev loops
```

Note: This also means removing the stale script reference and adding the skills directory to the tree.

- [ ] **Step 5: Check for any other references**

```bash
grep -rn "sync-commands\|update-commands" --include="*.md" . | grep -v "skills/sync-commands" | grep -v ".git/" | grep -v "docs/superpowers/plans/"
```

Fix any remaining references found.

- [ ] **Step 6: Commit the cleanup**

```bash
git add rules/CLAUDE.md README.md docs/FORMATS.md
git commit -m "Remove old sync/update commands, update references to skill"
```

---

### Task 4: Verify end-to-end

- [ ] **Step 1: Run the transform script from its new location**

```bash
python3 skills/sync-commands/transform.py
```

Expected: dry-run showing all 6 files as UNCHANGED (since we just synced).

- [ ] **Step 2: Verify skill is listed**

Check that the skill appears in the skills listing (the skill system auto-discovers `SKILL.md` files under `skills/`).

- [ ] **Step 3: Verify old commands are gone**

```bash
ls commands/
```

Expected: `cleanup.md`, `handoff.md`, `implement.md`, `plan.md`, `quick-fix.md`, `research.md`, `resume-handoff.md`, `review.md`, `validate-plan.md` — no `sync-commands.md` or `update-commands.md`.

- [ ] **Step 4: Verify no dangling references**

```bash
grep -rn "update-commands" --include="*.md" . | grep -v ".git/" | grep -v "skills/sync-commands" | grep -v "docs/superpowers/plans/"
grep -rn "scripts/sync-humanlayer" --include="*.md" . | grep -v ".git/" | grep -v "docs/superpowers/plans/"
```

Expected: no results.

- [ ] **Step 5: Final commit if any fixes needed**

```bash
git status
# If clean, no commit needed
```
