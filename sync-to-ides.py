#!/usr/bin/env python3
"""
Sync agents-config repository to Claude and Cursor IDE directories.

Creates symlinks FROM IDE directories TO repo, making repo the source of truth.
Warns before overwriting existing files.
"""

import argparse
import os
import sys
from pathlib import Path

# Mapping: (repo_path, claude_dest, cursor_dest, cursor_supported)
# cursor_supported indicates if Cursor actually reads this (TBD until verified)
SYNC_MAPPINGS = [
    ('rules/CLAUDE.md', '.claude/CLAUDE.md', None, False),  # Cursor doesn't use CLAUDE.md
    ('commands', '.claude/commands', '.cursor/commands', True),  # TBD - needs verification
    ('agents', '.claude/agents', '.cursor/agents', True),  # TBD - needs verification
    ('scripts/statusline-command.sh', '.claude/statusline-command.sh', None, False),  # Claude Code status line
    # Skills are added dynamically below — each subdir of skills/ gets its own symlink
    # so we don't clobber existing skills in ~/.claude/skills/ (e.g. marketing skills)
    # Rules (other than CLAUDE.md) are added dynamically below — each file in rules/
    # gets its own symlink to ~/.claude/rules/ so we don't clobber existing rules
]

HOME = Path.home()
REPO_DIR = Path.home() / '.agents-config'


def _discover_skills(repo_dir):
    """Auto-discover skill directories and add them to SYNC_MAPPINGS."""
    skills_dir = repo_dir / 'skills'
    if not skills_dir.is_dir():
        return
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and not child.name.startswith('.'):
            SYNC_MAPPINGS.append(
                (f'skills/{child.name}', f'.claude/skills/{child.name}', None, False)
            )


def _discover_rules(repo_dir):
    """Auto-discover rule files (excluding CLAUDE.md) and add them to SYNC_MAPPINGS."""
    rules_dir = repo_dir / 'rules'
    if not rules_dir.is_dir():
        return
    for child in sorted(rules_dir.iterdir()):
        if child.is_file() and child.suffix == '.md' and child.name != 'CLAUDE.md':
            SYNC_MAPPINGS.append(
                (f'rules/{child.name}', f'.claude/rules/{child.name}', None, False)
            )
CLAUDE_DIR = HOME / '.claude'
CURSOR_DIR = HOME / '.cursor'

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
        if target.exists():
            if target.is_symlink():
                current_target = target.readlink()
                if current_target.resolve() == source.resolve():
                    print(f"  ✓ Already linked: {target} -> {source}")
                    return True
                else:
                    print(f"  ♻ Would update: {target} -> {source} (currently -> {current_target})")
            else:
                print(f"  ⚠ Would overwrite: {target} (use --force)")
                return False
        else:
            print(f"  ✓ Would create: {target} -> {source}")
            return True
    
    # If target exists and is already correct symlink, skip
    if target.exists() and target.is_symlink():
        current_target = target.readlink()
        if current_target.resolve() == source.resolve():
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
            # For directories, preserve any IDE-specific files that might be inside
            # (though commands/agents shouldn't have IDE-specific files)
            import shutil
            preserve_items = []
            for item in target.iterdir():
                if item.name in CLAUDE_IGNORE:
                    preserve_items.append((item, target.parent / item.name))
                    print(f"    Preserving IDE file: {item.name}")
            
            # Remove directory
            shutil.rmtree(target)
            
            # Restore preserved files to parent directory
            for src, dst in preserve_items:
                if src.exists():  # Double-check it still exists
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


def verify_symlinks(ide=None):
    """Verify all symlinks are valid"""
    print("\nVerifying symlinks...")
    all_valid = True
    
    for repo_path, claude_dest, cursor_dest, cursor_supported in SYNC_MAPPINGS:
        source = REPO_DIR / repo_path
        
        # Check Claude symlink
        if ide in (None, 'claude', 'both'):
            claude_target = HOME / claude_dest
            if not claude_target.exists():
                print(f"  ✗ Missing: {claude_target}")
                all_valid = False
            elif not claude_target.is_symlink():
                print(f"  ✗ Not a symlink: {claude_target}")
                all_valid = False
            else:
                current_target = claude_target.readlink()
                if current_target.resolve() != source.resolve():
                    print(f"  ✗ Wrong target: {claude_target} -> {current_target} (expected {source})")
                    all_valid = False
                else:
                    print(f"  ✓ Valid: {claude_target} -> {source}")
        
        # Check Cursor symlink
        if ide in (None, 'cursor', 'both') and cursor_dest:
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
                    print(f"  ✓ Valid: {cursor_target} -> {source}")
    
    return all_valid


def main():
    global REPO_DIR
    parser = argparse.ArgumentParser(description='Sync agents-config repo to IDE directories')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files/directories')
    parser.add_argument('--verify', action='store_true', help='Only verify existing symlinks')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--ide', choices=['claude', 'cursor', 'both'], default='both',
                       help='Target specific IDE(s)')
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
    
    if args.verify:
        valid = verify_symlinks(args.ide)
        sys.exit(0 if valid else 1)
    
    print(f"Syncing from {REPO_DIR} to IDE directories...")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    for repo_path, claude_dest, cursor_dest, cursor_supported in SYNC_MAPPINGS:
        source = REPO_DIR / repo_path
        
        # Sync to Claude
        if args.ide in ('claude', 'both'):
            claude_target = HOME / claude_dest
            print(f"\nClaude: {repo_path} -> {claude_dest}")
            total_count += 1
            if create_symlink(source, claude_target, args.force, args.dry_run):
                success_count += 1
        
        # Sync to Cursor
        if args.ide in ('cursor', 'both') and cursor_dest:
            cursor_target = HOME / cursor_dest
            print(f"\nCursor: {repo_path} -> {cursor_dest}")
            if cursor_supported:
                total_count += 1
                result = create_symlink(source, cursor_target, args.force, args.dry_run)
                if result:
                    success_count += 1
            else:
                print(f"  ℹ Skipping (not supported by Cursor)")
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"Dry-run complete: {success_count}/{total_count} would be synced")
    else:
        print(f"Synced {success_count}/{total_count} files/directories")
    
    # Verify
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

