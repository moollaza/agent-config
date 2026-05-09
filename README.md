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
git clone <repo-url> ~/.agents-config
cd ~/.agents-config

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
├── plugins.json     # External skills/plugins registry (installed, not stored)
├── docs/            # Documentation
└── scripts/         # Utility scripts
```

## Syncing

The `sync-to-ides.py` script creates symlinks from IDE directories to this repo:

**Claude Code:**
- `~/.claude/CLAUDE.md` → `~/.agents-config/rules/CLAUDE.md`
- `~/.claude/commands/` → `~/.agents-config/commands/`
- `~/.claude/agents/` → `~/.agents-config/agents/`

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

## External Skills and Plugins

External skills and plugins are tracked in `plugins.json` but **not stored in this repo**. This keeps the repo lean while making setup reproducible.

- `plugins.json` — registry of skills/plugins to install (name, source, install command)
- `setup.sh` — installs them interactively during setup
- Skills/plugins live in the agent-specific directories managed by their installer, such as `~/.claude/skills/` for Claude Code skills

To add a skill or plugin, add an entry to `plugins.json` and re-run `./setup.sh`. Use `npx skills add ... -s <skill-name>` when an upstream repository contains multiple skills and only one should be installed.

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
