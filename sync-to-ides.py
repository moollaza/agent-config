#!/usr/bin/env python3
"""
Sync agents-config repository to Claude Code, Codex, and Cursor IDE directories.

Creates symlinks FROM IDE directories TO repo, making repo the source of truth.
Warns before overwriting existing files.

Codex (`~/.codex/AGENTS.md`) reads from the same source as Claude Code
(`~/.claude/CLAUDE.md`). Topic rule files mirror to `~/.codex/rules/` so the
cross-references in CLAUDE.md/AGENTS.md resolve identically for both agents.
"""

import argparse
import os
import sys
from pathlib import Path

# Mapping: (repo_path, claude_dest, cursor_dest, cursor_supported, codex_dest)
# - claude_dest:    path under HOME for Claude Code (None to skip)
# - cursor_dest:    path under HOME for Cursor (None to skip)
# - cursor_supported: whether Cursor actually consumes this (TBD until verified)
# - codex_dest:     path under HOME for Codex (None to skip)
SYNC_MAPPINGS = [
    # Claude Code's universal contract
    ('rules/CLAUDE.md', '.claude/CLAUDE.md', None, False, None),
    # Codex's contract: a small AGENTS.md that points at CLAUDE.md (mirrored to
    # ~/.codex/rules/CLAUDE.md via the rules auto-discovery below) plus the
    # Codex-only tool map. Keeps the always-on Claude Code prompt lean.
    ('rules/AGENTS.md', None, None, False, '.codex/AGENTS.md'),
    ('commands', '.claude/commands', '.cursor/commands', True, None),
    ('agents', '.claude/agents', '.cursor/agents', True, None),
    ('scripts/statusline-command.sh', '.claude/statusline-command.sh', None, False, None),
    # Skills: each subdir of skills/ gets its own symlink (added dynamically)
    # Rules other than CLAUDE.md and AGENTS.md: each file mirrors to .claude/rules/
    # AND .codex/rules/ via _discover_rules below
]

HOME = Path.home()
# Default to the directory this script lives in, so running the script from its
# repo location just works regardless of where the user cloned it.
REPO_DIR = Path(__file__).resolve().parent


def _discover_skills(repo_dir):
    """Auto-discover skill directories and add them to SYNC_MAPPINGS."""
    skills_dir = repo_dir / 'skills'
    if not skills_dir.is_dir():
        return
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and not child.name.startswith('.'):
            SYNC_MAPPINGS.append(
                (f'skills/{child.name}', f'.claude/skills/{child.name}', None, False, None)
            )


def _discover_rules(repo_dir):
    """Auto-discover rule files (excluding CLAUDE.md and AGENTS.md) and add them
    to SYNC_MAPPINGS.

    CLAUDE.md and AGENTS.md are root contracts — they're mapped explicitly to
    ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md respectively, not into rules/
    subdirectories. Every other rule file is mirrored to BOTH ~/.claude/rules/
    and ~/.codex/rules/ so cross-references inside the root contracts resolve
    for either agent.
    """
    rules_dir = repo_dir / 'rules'
    if not rules_dir.is_dir():
        return
    # Skip root contracts (mapped explicitly above) and any local-only rules
    # listed in .gitignore — those must never sync to other agents.
    skip = {'CLAUDE.md', 'AGENTS.md', 'asana-data-protection.md'}
    for child in sorted(rules_dir.iterdir()):
        if child.is_file() and child.suffix == '.md' and child.name not in skip:
            SYNC_MAPPINGS.append((
                f'rules/{child.name}',
                f'.claude/rules/{child.name}',
                None,
                False,
                f'.codex/rules/{child.name}',
            ))


CLAUDE_DIR = HOME / '.claude'
CURSOR_DIR = HOME / '.cursor'
CODEX_DIR = HOME / '.codex'

# Files/directories to preserve in IDE directories (Claude-specific)
CLAUDE_IGNORE = {
    'debug', 'file-history', 'history.jsonl', 'ide', 'plugins',
    'projects', 'shell-snapshots', 'statsig',
    'todos', 'session-env', 'settings.json'
}


def create_symlink(source, target, force=False, dry_run=False):
    """Create symlink from source to target, handling existing links/files.

    Preserves IDE-specific files when removing directories in .claude.
    """
    source = Path(source)
    target = Path(target)

    if not source.exists():
        print(f"  ⚠ Source does not exist: {source}")
        return False

    if dry_run:
        if target.is_symlink():
            current_target = target.readlink()
            if target.exists() and current_target.resolve() == source.resolve():
                print(f"  ✓ Already linked: {target} -> {source}")
                return True
            else:
                print(f"  ♻ Would update: {target} -> {source} (currently -> {current_target})")
                return True
        elif target.exists():
            print(f"  ⚠ Would overwrite: {target} (use --force)")
            return False
        else:
            print(f"  ✓ Would create: {target} -> {source}")
            return True

    # Handle existing symlinks (including broken ones)
    if target.is_symlink():
        current_target = target.readlink()
        if target.exists() and current_target.resolve() == source.resolve():
            return True
        print(f"  ♻ Removing existing symlink: {target}")
        target.unlink()
    elif target.exists():
        print(f"  ⚠ Target exists but is not a symlink: {target}")
        if not force:
            print(f"    Use --force to overwrite")
            return False
        print(f"  ♻ Removing existing file/directory: {target}")
        if target.is_dir():
            import shutil
            preserve_items = []
            for item in target.iterdir():
                if item.name in CLAUDE_IGNORE:
                    preserve_items.append((item, target.parent / item.name))
                    print(f"    Preserving IDE file: {item.name}")

            shutil.rmtree(target)

            for src, dst in preserve_items:
                if src.exists():
                    import shutil
                    shutil.move(str(src), str(dst))
        else:
            target.unlink()

    # Create parent directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    # Create symlink
    try:
        target.symlink_to(source)
        print(f"  ✓ Created: {target} -> {source}")
        return True
    except OSError as e:
        print(f"  ✗ Failed to create symlink: {e}")
        return False


def _check_one_symlink(label, target, source):
    """Verify one symlink. Returns True iff valid (or absent-and-optional)."""
    if not target.exists():
        print(f"  ✗ Missing: {target}")
        return False
    if not target.is_symlink():
        print(f"  ✗ Not a symlink: {target}")
        return False
    current_target = target.readlink()
    if current_target.resolve() != source.resolve():
        print(f"  ✗ Wrong target: {target} -> {current_target} (expected {source})")
        return False
    print(f"  ✓ Valid ({label}): {target} -> {source}")
    return True


def verify_symlinks(ide=None):
    """Verify all symlinks are valid"""
    print("\nVerifying symlinks...")
    all_valid = True

    for repo_path, claude_dest, cursor_dest, cursor_supported, codex_dest in SYNC_MAPPINGS:
        source = REPO_DIR / repo_path

        # Claude
        if claude_dest and ide in (None, 'all', 'claude', 'both'):
            if not _check_one_symlink('claude', HOME / claude_dest, source):
                all_valid = False

        # Codex
        if codex_dest and ide in (None, 'all', 'codex'):
            if not _check_one_symlink('codex', HOME / codex_dest, source):
                all_valid = False

        # Cursor
        if cursor_dest and ide in (None, 'all', 'cursor', 'both'):
            cursor_target = HOME / cursor_dest
            if not cursor_target.exists():
                print(f"  ⚠ Missing: {cursor_target} (may not be supported by Cursor)")
            elif not cursor_target.is_symlink():
                print(f"  ✗ Not a symlink: {cursor_target}")
                all_valid = False
            else:
                current_target = cursor_target.readlink()
                if current_target.resolve() != source.resolve():
                    print(f"  ✗ Wrong target: {cursor_target} -> {current_target} (expected {source})")
                    all_valid = False
                else:
                    print(f"  ✓ Valid (cursor): {cursor_target} -> {source}")

    return all_valid


def main():
    global REPO_DIR
    parser = argparse.ArgumentParser(description='Sync agents-config repo to IDE directories')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files/directories')
    parser.add_argument('--verify', action='store_true', help='Only verify existing symlinks')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--ide', choices=['claude', 'cursor', 'codex', 'both', 'all'], default='all',
                       help="Target IDE(s). 'both' = claude+cursor (legacy); 'all' = claude+cursor+codex")
    parser.add_argument('--repo-dir', type=str, default=str(REPO_DIR),
                       help=f'Repository directory (default: {REPO_DIR})')
    args = parser.parse_args()

    REPO_DIR = Path(args.repo_dir).expanduser()

    if not REPO_DIR.exists():
        print(f"Error: Repository directory does not exist: {REPO_DIR}")
        sys.exit(1)

    # Discover skills subdirectories and rules files, add to mappings
    _discover_skills(REPO_DIR)
    _discover_rules(REPO_DIR)

    # Ensure IDE directories exist
    CLAUDE_DIR.mkdir(exist_ok=True)
    CURSOR_DIR.mkdir(exist_ok=True)
    CODEX_DIR.mkdir(exist_ok=True)

    if args.verify:
        valid = verify_symlinks(args.ide)
        sys.exit(0 if valid else 1)

    print(f"Syncing from {REPO_DIR} to IDE directories...")
    print("=" * 60)

    success_count = 0
    total_count = 0

    for repo_path, claude_dest, cursor_dest, cursor_supported, codex_dest in SYNC_MAPPINGS:
        source = REPO_DIR / repo_path

        # Sync to Claude
        if claude_dest and args.ide in ('claude', 'both', 'all'):
            claude_target = HOME / claude_dest
            print(f"\nClaude: {repo_path} -> {claude_dest}")
            total_count += 1
            if create_symlink(source, claude_target, args.force, args.dry_run):
                success_count += 1

        # Sync to Codex
        if codex_dest and args.ide in ('codex', 'all'):
            codex_target = HOME / codex_dest
            print(f"\nCodex:  {repo_path} -> {codex_dest}")
            total_count += 1
            if create_symlink(source, codex_target, args.force, args.dry_run):
                success_count += 1

        # Sync to Cursor
        if cursor_dest and args.ide in ('cursor', 'both', 'all'):
            cursor_target = HOME / cursor_dest
            print(f"\nCursor: {repo_path} -> {cursor_dest}")
            if cursor_supported:
                total_count += 1
                if create_symlink(source, cursor_target, args.force, args.dry_run):
                    success_count += 1
            else:
                print(f"  ℹ Skipping (not supported by Cursor)")

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"Dry-run complete: {success_count}/{total_count} would be synced")
    else:
        print(f"Synced {success_count}/{total_count} files/directories")

    if not args.dry_run:
        print("\n" + "=" * 60)
        if verify_symlinks(args.ide):
            print("\n✓ All symlinks verified successfully")
            return 0
        else:
            print("\n✗ Some symlinks are invalid")
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
