#!/bin/bash
# sync.sh — single entry point for agents-config.
#
# 1. Syncs symlinks (AGENTS.md -> ~/.claude/CLAUDE.md, ~/.codex/AGENTS.md, skills).
# 2. Installs every skill listed in plugins.json (so new entries land).
# 3. Updates all installed skills to their latest upstream versions.
#
# Non-interactive — re-run anytime to refresh everything to latest upstream.
#
# Usage:
#   ./sync.sh            sync symlinks, install + update skills
#   ./sync.sh --dry-run  preview every action without changing anything

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

DRY_RUN=""
case "${1:-}" in
    "") ;;
    --dry-run) DRY_RUN="1" ;;
    -h|--help) echo "Usage: ./sync.sh [--dry-run]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; echo "Usage: ./sync.sh [--dry-run]" >&2; exit 2 ;;
esac

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found" >&2
    exit 1
fi

failed=0

echo "Syncing agents-config${DRY_RUN:+ (dry-run)}..."
echo "======================================"

# 1. Symlinks
echo ""
echo "▸ Symlinks"
if [ -n "$DRY_RUN" ]; then
    python3 sync-to-ides.py --dry-run
else
    python3 sync-to-ides.py || { echo "  ⚠ symlink sync reported problems" >&2; failed=1; }
fi

# 2. Install every skill tracked in plugins.json (ensures new entries land).
echo ""
echo "▸ Skills (plugins.json)"
if [ -f plugins.json ]; then
    # Install strings come from a JSON file that a malicious PR could tamper with.
    # Parse with shlex, require the command to be `npx skills ...`, then run via an
    # argv list (no shell). Per-skill failures are non-fatal but flip the exit code.
    DRY_RUN="$DRY_RUN" python3 <<'PY' || failed=1
import json, os, shlex, subprocess, sys

dry = bool(os.environ.get("DRY_RUN"))
plugins = json.load(open("plugins.json"))["plugins"]
print(f"  {len(plugins)} skill(s) tracked")

rc = 0
for p in plugins:
    name, install = p["name"], p["install"]
    try:
        argv = shlex.split(install)
    except ValueError as e:
        print(f"  ✗ {name}: cannot parse install command ({e})", file=sys.stderr); rc = 1; continue
    if argv[:2] != ["npx", "skills"]:
        print(f"  ✗ {name}: install must start with `npx skills` (got: {install!r})", file=sys.stderr); rc = 1; continue
    if dry:
        print(f"  • would run: {install}"); continue
    print(f"  → {name}")
    result = subprocess.run(argv, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ {name} failed: {result.stderr.strip()}", file=sys.stderr); rc = 1

sys.exit(rc)
PY
else
    echo "  no plugins.json found, skipping"
fi

# 3. Update every installed skill to its latest upstream version.
echo ""
echo "▸ Update to latest upstream"
if [ -n "$DRY_RUN" ]; then
    echo "  • would run: npx skills update -g -y"
else
    npx skills update -g -y || { echo "  ⚠ skill update reported problems" >&2; failed=1; }
fi

echo ""
if [ -n "$DRY_RUN" ]; then
    echo "Dry-run complete — nothing changed."
elif [ "$failed" -eq 0 ]; then
    echo "✓ Sync complete."
else
    echo "✗ Sync finished with problems (see above)." >&2
fi
exit "$failed"
