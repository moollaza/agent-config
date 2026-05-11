#!/usr/bin/env python3
"""
Sync agents-config repository to Claude Code and Codex.

Creates symlinks FROM ~/.claude/ and ~/.codex/ TO this repo, making the repo
the source of truth. Warns before overwriting existing files.

Codex's `~/.codex/AGENTS.md` is a small tool-map file; it instructs Codex to
also read `~/.codex/CLAUDE.md` (which symlinks to the same universal contract
Claude Code reads at `~/.claude/CLAUDE.md`).
"""

import argparse
import sys
from pathlib import Path

# Mapping: (repo_path, claude_dest, codex_dest)
# - claude_dest: path under HOME for Claude Code (None to skip)
# - codex_dest:  path under HOME for Codex (None to skip)
SYNC_MAPPINGS = [
    # Universal contract — same source, exposed to both agents
    ('CLAUDE.md', '.claude/CLAUDE.md', '.codex/CLAUDE.md'),
    # Codex tool-map — Codex-only
    ('AGENTS.md', None, '.codex/AGENTS.md'),
    ('scripts/statusline-command.sh', '.claude/statusline-command.sh', None),
    # Skills: each subdir of skills/ gets its own symlink (added dynamically)
]

HOME = Path.home()
# Default to the directory this script lives in, so running it from its repo
# location just works regardless of where the user cloned it.
REPO_DIR = Path(__file__).resolve().parent

CLAUDE_DIR = HOME / '.claude'
CODEX_DIR = HOME / '.codex'

# Files/directories to preserve in IDE directories (Claude-specific)
CLAUDE_IGNORE = {
    'debug', 'file-history', 'history.jsonl', 'ide', 'plugins',
    'projects', 'shell-snapshots', 'statsig',
    'todos', 'session-env', 'settings.json'
}


def _discover_skills(repo_dir):
    """Auto-discover skill directories and add them to SYNC_MAPPINGS."""
    skills_dir = repo_dir / 'skills'
    if not skills_dir.is_dir():
        return
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and not child.name.startswith('.'):
            SYNC_MAPPINGS.append(
                (f'skills/{child.name}', f'.claude/skills/{child.name}', None)
            )


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
            print(f"  ♻ Would update: {target} -> {source} (currently -> {current_target})")
            return True
        elif target.exists():
            print(f"  ⚠ Would overwrite: {target} (use --force)")
            return False
        else:
            print(f"  ✓ Would create: {target} -> {source}")
            return True

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
                    shutil.move(str(src), str(dst))
        else:
            target.unlink()

    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        target.symlink_to(source)
        print(f"  ✓ Created: {target} -> {source}")
        return True
    except OSError as e:
        print(f"  ✗ Failed to create symlink: {e}")
        return False


def _cleanup_stale_symlinks(dry_run=False):
    """Remove broken IDE-side symlinks whose source has been deleted from the repo.

    Covers `~/.claude/skills/` (a removed skill leaves a dangling symlink) and
    `~/.claude/rules/` / `~/.codex/rules/` (historical topic-file locations
    that may still hold dangling symlinks from before they were flattened).
    """
    for ide_dir in (CLAUDE_DIR / 'rules', CODEX_DIR / 'rules', CLAUDE_DIR / 'skills'):
        if not ide_dir.is_dir():
            continue
        for entry in ide_dir.iterdir():
            if not entry.is_symlink():
                continue
            try:
                target = entry.readlink()
            except OSError:
                continue
            resolved = (entry.parent / target).resolve() if not target.is_absolute() else target.resolve()
            if not resolved.exists():
                if dry_run:
                    print(f"  ♻ Would remove stale symlink: {entry} -> {target}")
                else:
                    print(f"  ♻ Removing stale symlink: {entry} -> {target}")
                    entry.unlink()


def _check_one_symlink(label, target, source):
    """Verify one symlink. Returns True iff valid."""
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
    """Verify all symlinks are valid."""
    print("\nVerifying symlinks...")
    all_valid = True

    for repo_path, claude_dest, codex_dest in SYNC_MAPPINGS:
        source = REPO_DIR / repo_path

        if claude_dest and ide in (None, 'all', 'claude'):
            if not _check_one_symlink('claude', HOME / claude_dest, source):
                all_valid = False

        if codex_dest and ide in (None, 'all', 'codex'):
            if not _check_one_symlink('codex', HOME / codex_dest, source):
                all_valid = False

    return all_valid


def main():
    global REPO_DIR
    parser = argparse.ArgumentParser(description='Sync agents-config repo to IDE directories')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files/directories')
    parser.add_argument('--verify', action='store_true', help='Only verify existing symlinks')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--ide', choices=['claude', 'codex', 'all'], default='all',
                       help="Target IDE(s). Default: all (claude + codex).")
    parser.add_argument('--repo-dir', type=str, default=str(REPO_DIR),
                       help=f'Repository directory (default: {REPO_DIR})')
    args = parser.parse_args()

    REPO_DIR = Path(args.repo_dir).expanduser()

    if not REPO_DIR.exists():
        print(f"Error: Repository directory does not exist: {REPO_DIR}")
        sys.exit(1)

    _discover_skills(REPO_DIR)

    CLAUDE_DIR.mkdir(exist_ok=True)
    CODEX_DIR.mkdir(exist_ok=True)

    if args.verify:
        valid = verify_symlinks(args.ide)
        sys.exit(0 if valid else 1)

    _cleanup_stale_symlinks(args.dry_run)

    print(f"Syncing from {REPO_DIR} to IDE directories...")
    print("=" * 60)

    success_count = 0
    total_count = 0

    for repo_path, claude_dest, codex_dest in SYNC_MAPPINGS:
        source = REPO_DIR / repo_path

        if claude_dest and args.ide in ('claude', 'all'):
            claude_target = HOME / claude_dest
            print(f"\nClaude: {repo_path} -> {claude_dest}")
            total_count += 1
            if create_symlink(source, claude_target, args.force, args.dry_run):
                success_count += 1

        if codex_dest and args.ide in ('codex', 'all'):
            codex_target = HOME / codex_dest
            print(f"\nCodex:  {repo_path} -> {codex_dest}")
            total_count += 1
            if create_symlink(source, codex_target, args.force, args.dry_run):
                success_count += 1

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
