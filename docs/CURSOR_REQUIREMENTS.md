# Cursor IDE Requirements

Based on [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)

## Directory Structure

Cursor uses `.cursor/` directory structure, but primarily at the **project level**:

### Project-Level Configuration

Within each project root:
- `.cursor/rules/` directory with `.mdc` files
- `AGENTS.md` file in project root (alternative to `.cursor/rules/`)
- `.cursorrules` file (legacy, deprecated)

### Global Configuration

**From Cursor Documentation:**
- User rules defined in Cursor settings (applies across all projects)
- Global configuration location: `~/.cursor/` for IDE state

**To Verify:**
- Does Cursor read global `~/.cursor/commands/` directory?
- Does Cursor read global `~/.cursor/agents/` directory?
- Does Cursor support global `~/.cursor/rules/` directory?

## Current Observation

Current symlinks exist:
- `~/.cursor/CLAUDE.md` → `~/.claude/CLAUDE.md` (likely not used by Cursor)
- `~/.cursor/commands/` → `~/.claude/commands/` (needs verification)
- `~/.cursor/agents/` → `~/.claude/agents/` (needs verification)

**Note:** Cursor does NOT use `CLAUDE.md` filename. Cursor uses:
- Project-level `.cursor/rules/` directory
- Project-level `AGENTS.md` file
- User settings for global rules

## Testing Needed

1. Verify if Cursor reads from `~/.cursor/commands/` globally
2. Verify if Cursor reads from `~/.cursor/agents/` globally
3. Determine if Cursor supports global `.cursor/rules/` directory
4. Test if symlinks work correctly with Cursor

## Format Differences

- Cursor uses `.mdc` format for rules files (in `.cursor/rules/`)
- Claude uses `.md` format for all files
- Both use Markdown syntax, but Cursor may prefer `.mdc` extension

