#!/usr/bin/env python3
"""Sync agents-config to ~/.claude/ and ~/.codex/ via symlinks.

Touch ~/.claude/optional to additionally sync OPTIONAL_SKILLS and
optional-context.md. Re-running without the sentinel removes them.

Usage: python3 sync-to-ides.py [--dry-run] [--force]
  --dry-run  preview, change nothing
  --force    overwrite real (non-symlink) files at the target
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOME = Path.home()
SENTINEL = HOME / '.claude' / 'optional'

# Keep in sync with OPTIONAL_PLUGINS in setup.sh.
OPTIONAL_SKILLS = frozenset({'secrets', 'swarm-claim'})

DRY = '--dry-run' in sys.argv[1:]
FORCE = '--force' in sys.argv[1:]


def link(src: Path, dst: Path) -> None:
    """Symlink src → dst. Refuses to clobber a real file unless --force."""
    if dst.is_symlink() and dst.resolve() == src.resolve():
        return  # already correct
    if dst.exists() and not dst.is_symlink():
        if not FORCE:
            print(f"  ⚠ skip (real file, use --force): {dst}")
            return
        print(f"  ♻ overwrite real file: {dst}")
        if not DRY:
            dst.unlink()
    print(f"  → {dst} -> {src}")
    if DRY:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink():
        dst.unlink()
    dst.symlink_to(src)


def unlink_if_into_repo(dst: Path) -> None:
    """Remove dst if it's a symlink pointing into REPO (i.e. ours to evict)."""
    if not dst.is_symlink():
        return
    try:
        if REPO not in dst.resolve().parents:
            return
    except OSError:
        return
    print(f"  ✗ remove (no sentinel): {dst}")
    if not DRY:
        dst.unlink()


def main() -> int:
    optional = SENTINEL.exists()
    flags = ', '.join(f for f, on in [('dry-run', DRY), ('force', FORCE)] if on)
    print(f"Mode: {'optional' if optional else 'default'}" + (f" [{flags}]" if flags else ''))

    link(REPO / 'AGENTS.md', HOME / '.claude/CLAUDE.md')
    link(REPO / 'AGENTS.md', HOME / '.codex/AGENTS.md')
    link(REPO / 'scripts/statusline-command.sh', HOME / '.claude/statusline-command.sh')

    for skill in sorted((REPO / 'skills').iterdir()):
        if not skill.is_dir() or skill.name.startswith('.'):
            continue
        dst = HOME / '.claude/skills' / skill.name
        if not optional and skill.name in OPTIONAL_SKILLS:
            unlink_if_into_repo(dst)
        else:
            link(skill, dst)

    ctx_dst = HOME / '.claude/rules/optional-context.md'
    if optional:
        link(REPO / 'optional-context.md', ctx_dst)
    else:
        unlink_if_into_repo(ctx_dst)

    return 0


if __name__ == '__main__':
    sys.exit(main())
