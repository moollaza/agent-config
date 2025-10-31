# Setup Guide

Detailed setup instructions for agents-config repository.

## Prerequisites

- Python 3.6+
- Git
- Claude Code and/or Cursor IDE installed

## Initial Setup

### 1. Clone Repository

```bash
git clone <repo-url> ~/agents-config
cd ~/agents-config
```

### 2. Review Changes

Run a dry-run to see what will be synced:

```bash
python3 sync-to-ides.py --dry-run
```

This shows:
- What symlinks will be created
- What files will be overwritten (if any)
- IDE-specific mappings

### 3. Apply Changes

Option A - Interactive setup:
```bash
./setup.sh
```

Option B - Manual sync:
```bash
# With warnings (prompts before overwriting)
python3 sync-to-ides.py

# Force overwrite (no prompts)
python3 sync-to-ides.py --force
```

### 4. Verify Setup

```bash
python3 sync-to-ides.py --verify
```

## IDE-Specific Setup

### Claude Code

Claude automatically reads from:
- `~/.claude/CLAUDE.md` - Global rules
- `~/.claude/commands/` - Command definitions
- `~/.claude/agents/` - Agent definitions

After syncing, these will be symlinks pointing to the repo.

### Cursor IDE

Cursor configuration:
- Global `~/.cursor/commands/` and `~/.cursor/agents/` may be supported (needs verification)
- Cursor primarily uses project-level `.cursor/rules/` directory
- See `docs/CURSOR_REQUIREMENTS.md` for details

## Adding New Files

1. Add file to repository:
   ```bash
   # Add new command
   cp new-command.md ~/agents-config/commands/
   
   # Add new agent
   cp new-agent.md ~/agents-config/agents/
   ```

2. Sync to IDEs:
   ```bash
   python3 sync-to-ides.py
   ```

3. Commit changes:
   ```bash
   git add commands/new-command.md
   git commit -m "Add new-command"
   ```

## Updating Existing Files

1. Edit files directly in `~/agents-config/`
2. Changes are immediately available via symlinks
3. Commit changes:
   ```bash
   git add rules/CLAUDE.md
   git commit -m "Update rules"
   ```

## Multi-Machine Setup

1. Clone repo on new machine:
   ```bash
   git clone <repo-url> ~/agents-config
   ```

2. Run setup:
   ```bash
   cd ~/agents-config
   ./setup.sh
   ```

3. Pull updates:
   ```bash
   cd ~/agents-config
   git pull
   # Symlinks automatically point to latest files
   ```

## Troubleshooting

### Symlinks Not Working

If symlinks don't work (rare on Linux/Mac):
- Check filesystem supports symlinks
- Verify permissions on directories
- Try running with `--force` flag

### Files Modified in IDE Directories

If files were modified directly in IDE directories:
- Remove modified files
- Re-run sync script
- Future edits should be made in repo only

### Verify Symlink Integrity

```bash
python3 sync-to-ides.py --verify
```

This checks:
- All symlinks exist
- Symlinks point to correct locations
- No broken symlinks

## Best Practices

1. **Always edit in repo** - Never edit files directly in `~/.claude/` or `~/.cursor/`
2. **Commit frequently** - Keep repo in sync with git
3. **Verify after changes** - Run `--verify` after setup
4. **Document additions** - Update `docs/FORMATS.md` when adding new file types

