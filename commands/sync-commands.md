# Sync Commands from Upstream

Sync commands from humanlayer upstream and audit changes for local convention compliance.

## Process

### Step 1: Pull latest from origin
```bash
git pull origin main
```

### Step 2: Run the sync script
```bash
python3 scripts/sync-humanlayer-commands.py --apply --yes
```

### Step 3: Audit changes for local conventions

After syncing, check for issues that need fixing:

1. **Command references** - Ensure command names use dashes not underscores:
   - `/resume-handoff` NOT `/resume_handoff`
   - `/validate-plan` NOT `/validate_plan`

   Check with:
   ```bash
   grep -n "resume_handoff\|validate_plan" commands/*.md
   ```

2. **Directory references** - This repo uses `agent-docs/` not `thoughts/`:
   - `agent-docs/` NOT `thoughts/`
   - `agent-docs-locator` NOT `thoughts-locator`
   - `agent-docs-analyzer` NOT `thoughts-analyzer`

   Check with:
   ```bash
   grep -n "thoughts" commands/*.md | grep -v update-commands.md
   ```
   Note: `update-commands.md` legitimately references `thoughts` in its transformation rules.

3. **Path references** - Ensure paths match local structure:
   - Plans: `agent-docs/shared/plans/`
   - Tickets: `agent-docs/*/tickets/`

### Step 4: Fix any issues found

Use Edit tool to fix any convention violations found in Step 3.

### Step 5: Review and commit

1. Check what changed:
   ```bash
   git diff --stat
   git diff
   ```

2. If changes look good, commit:
   ```bash
   git add commands/*.md
   git commit -m "Sync commands from humanlayer upstream"
   ```

## Local Conventions Reference

| Upstream (humanlayer) | Local (this repo) |
|-----------------------|-------------------|
| `thoughts/` | `agent-docs/` |
| `thoughts-locator` | `agent-docs-locator` |
| `thoughts-analyzer` | `agent-docs-analyzer` |
| `/resume_handoff` | `/resume-handoff` |
| `/create_plan` | `/plan` |
| `/implementation_plan` | `/plan` |

## When to Run

- Periodically to pick up upstream improvements
- After hearing about new features in humanlayer commands
- When commands feel outdated or missing functionality
