#!/bin/bash
# Setup script for agents-config repository

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Setting up agents-config repository..."
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found"
    exit 1
fi

# Run sync script with dry-run first
echo "Previewing changes..."
python3 sync-to-ides.py --dry-run

echo ""
read -p "Apply these changes? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 sync-to-ides.py
    echo ""
    echo "Symlinks synced!"
else
    echo "Symlink setup cancelled."
    exit 1
fi

# Install external skills/plugins from plugins.json
echo ""
echo "External skills/plugins"
echo "======================================"
if [ -f plugins.json ]; then
    # Heredoc with single-quoted delimiter — no shell or Python interpolation.
    # plugins.json is read via relative path because we cd'd to SCRIPT_DIR above.
    python3 <<'PY'
import json
plugins = json.load(open('plugins.json'))['plugins']
print(f"Found {len(plugins)} external item(s) in plugins.json:")
print()
for p in plugins:
    print(f"  - {p['name']}: {p['description']}")
    print(f"      $ {p['install']}")
PY
    echo ""
    read -p "Install external skills/plugins? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # shell=True is unsafe — install strings come from a JSON file that
        # could be tampered with via a malicious PR. Parse with shlex, enforce
        # the command is `npx skills ...`, then call subprocess.run with an
        # argv list (no shell). Per-plugin failures are non-fatal.
        python3 <<'PY'
import json, shlex, subprocess, sys

plugins = json.load(open('plugins.json'))['plugins']

for p in plugins:
    name = p['name']
    install = p['install']
    try:
        argv = shlex.split(install)
    except ValueError as e:
        print(f"  ✗ {name} skipped: cannot parse install command ({e})", file=sys.stderr)
        continue

    if len(argv) < 2 or argv[0] != 'npx' or argv[1] != 'skills':
        print(f"  ✗ {name} skipped: install must start with `npx skills` (got: {install!r})", file=sys.stderr)
        continue

    print(f"Installing {name}...")
    result = subprocess.run(argv, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ {name} installed")
    else:
        print(f"  ✗ {name} failed: {result.stderr.strip()}", file=sys.stderr)
PY
    else
        echo "External install skipped."
    fi
else
    echo "No plugins.json found, skipping."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To verify symlinks:"
echo "  python3 sync-to-ides.py --verify"
