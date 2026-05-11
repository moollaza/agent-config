# agents-config

Centralized configuration repository for Claude Code and Codex.

## Overview

Single source of truth for:
- Assistant rules — `CLAUDE.md` (Claude Code's contract, also read by Codex) and `AGENTS.md` (Codex tool-map)
- Local skills (`skills/`) and external skill registry (`plugins.json`)

Files are symlinked into IDE directories — never edit `~/.claude/` or `~/.codex/` paths directly.

## Authoring philosophy

The contract is **a small set of numbered guidelines** — high-level direction on how the agent should behave plus explicit guards against the user's known bad habits. No topic files, no progressive-disclosure breadcrumbs, no operational templates that the agent would already produce on its own.

Inspired by [Matt Pocock's AGENTS.md guide](https://www.aihero.dev/a-complete-guide-to-agents-md):

- Keep the always-loaded contract lean — every token loads on every request.
- Each rule must earn its keep: name a specific failure mode that breaks if the rule is removed.
- Trust senior-engineer judgment for everything else.

If a rule emerges that needs detail (templates, checklists, protocols), prefer adding a feedback memory at `~/.claude/projects/<encoded-cwd>/memory/` over reintroducing topic files — memory loads automatically and stays close to the rules in spirit.

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
├── CLAUDE.md        # 11-bullet universal contract (Claude Code + Codex both read)
├── AGENTS.md        # Codex-specific tool-map; points at CLAUDE.md
├── skills/          # Local skills (synced via symlinks)
├── plugins.json     # External skills/plugins registry (installed, not stored)
├── docs/            # Documentation
└── scripts/         # Utility scripts
```

## Syncing

`sync-to-ides.py` creates symlinks from IDE directories to this repo, and removes any stale symlinks whose source has been deleted.

**Claude Code (`~/.claude/`):**
- `CLAUDE.md` → repo `CLAUDE.md`
- `skills/<each>` → matching repo paths

**Codex (`~/.codex/`):**
- `CLAUDE.md` → repo `CLAUDE.md` (same universal contract)
- `AGENTS.md` → repo `AGENTS.md` (tool-map; instructs Codex to read `CLAUDE.md` first)

## Usage

```bash
# Preview changes
python3 sync-to-ides.py --dry-run

# Apply (default targets both Claude Code and Codex)
python3 sync-to-ides.py

# Force overwrite (replaces real files with symlinks)
python3 sync-to-ides.py --force

# Target specific IDE
python3 sync-to-ides.py --ide=claude
python3 sync-to-ides.py --ide=codex

# Verify symlinks
python3 sync-to-ides.py --verify
```

## Making Changes

1. Edit files in this repository
2. Changes are immediately available via symlinks
3. Commit changes to git
4. Pull updates on other machines

## External Skills and Plugins

External skills and plugins are tracked in `plugins.json` but **not stored in this repo**. This keeps the repo lean while making setup reproducible.

- `plugins.json` — registry of skills/plugins to install (name, source, install command)
- `setup.sh` — installs them interactively during setup
- Skills/plugins live in the agent-specific directories managed by their installer, such as `~/.claude/skills/` for Claude Code skills

To add a skill or plugin, add an entry to `plugins.json` and re-run `./setup.sh`. Use `npx skills add ... -s <skill-name>` when an upstream repository contains multiple skills and only one should be installed.

## IDE-Specific Notes

### Claude Code
- Reads `~/.claude/CLAUDE.md` for global rules (the 11-bullet contract).
- Reads `skills/` directory.

### Codex
- Reads `~/.codex/AGENTS.md` first — small file that points at `~/.codex/CLAUDE.md` for the universal contract.
- The `<!-- BEGIN COMPOUND CODEX TOOL MAP -->` block in `AGENTS.md` is auto-managed by the Compound Engineering plugin and translates Claude Code tool names to Codex equivalents.

## Documentation

- `docs/SETUP.md` - Detailed setup guide
