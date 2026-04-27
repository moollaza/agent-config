# agents-config

Centralized configuration repository for Claude Code and Cursor IDE.

## Overview

This repository serves as the single source of truth for:
- Assistant rules
- Command definitions
- Agent definitions

Files are synced to IDE directories via symlinks, ensuring consistency and preventing direct modification of IDE directories.

## Quick Start

```bash
# Clone the repository
git clone <repo-url> ~/projects/agent-config
cd ~/projects/agent-config

# Sync to IDE directories (dry-run first)
python3 sync-to-ides.py --dry-run

# Apply changes
python3 sync-to-ides.py

# Or use setup script
./setup.sh
```

## Structure

```
.agents-config/
├── rules/           # Assistant rules (Claude uses CLAUDE.md)
├── commands/        # Command definitions
├── agents/          # Agent definitions
├── skills/          # Local skills (synced via symlinks)
├── plugins.json     # External plugin registry (installed, not stored)
├── docs/            # Documentation
└── scripts/         # Utility scripts
```

## Syncing

The `sync-to-ides.py` script creates symlinks from IDE directories to this repo:

**Claude Code:**
- `~/.claude/CLAUDE.md` → `<repo>/rules/CLAUDE.md`
- `~/.claude/commands/` → `<repo>/commands/`
- `~/.claude/agents/` → `<repo>/agents/`
- `~/.claude/skills/<skill-name>/` → `<repo>/skills/<skill-name>/`

**Cursor IDE:**
- `~/.cursor/commands/` → `~/.agents-config/commands/` (if supported)
- `~/.cursor/agents/` → `~/.agents-config/agents/` (if supported)

## Usage

```bash
# Preview changes
python3 sync-to-ides.py --dry-run

# Apply changes (with warnings)
python3 sync-to-ides.py

# Force overwrite
python3 sync-to-ides.py --force

# Target specific IDE
python3 sync-to-ides.py --ide=claude
python3 sync-to-ides.py --ide=cursor

# Verify symlinks
python3 sync-to-ides.py --verify
```

## Making Changes

1. Edit files in this repository
2. Changes are immediately available via symlinks
3. Commit changes to git
4. Pull updates on other machines

## Syncing Commands from Upstream

Commands are synced from `humanlayer/humanlayer@main/.claude/commands`. Use the `sync-commands` skill which runs the bundled transform script and audits for convention compliance.

## External Plugins

External plugins are tracked in `plugins.json` but **not stored in this repo**. This keeps the repo lean while making setup reproducible.

- `plugins.json` — registry of plugins to install (name, source, install command)
- `setup.sh` — installs them interactively during setup
- Plugins live in `~/.claude/plugins/` (managed by Claude Code)

To add a plugin, add an entry to `plugins.json` and re-run `./setup.sh`.

## IDE-Specific Notes

### Claude Code
- Uses `CLAUDE.md` for global rules
- Reads `commands/` and `agents/` directories
- Supports `.md` file format

### Cursor IDE
- Does NOT use `CLAUDE.md` filename
- Primarily uses project-level `.cursor/rules/` directory
- Global support for `commands/` and `agents/` needs verification
- See `docs/CURSOR_REQUIREMENTS.md` for details

## Documentation

- `docs/FORMATS.md` - File format documentation
- `docs/CURSOR_REQUIREMENTS.md` - Cursor-specific requirements
- `docs/SETUP.md` - Detailed setup guide
