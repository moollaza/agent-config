#!/bin/bash
# Setup script for agents-config repository

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Setting up agents-config repository..."
echo "======================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found"
    exit 1
fi

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

# Install external skills/plugins from plugins.json, gated by ~/.claude/optional.
echo ""
echo "External skills/plugins"
echo "======================================"
if [ -f plugins.json ]; then
    if [ -f "$HOME/.claude/optional" ]; then
        OPTIONAL=1
        echo "Mode: optional (sentinel found)"
    else
        OPTIONAL=0
        echo "Mode: default (no $HOME/.claude/optional sentinel)"
    fi
    echo ""

    # Single-quoted heredoc blocks interpolation; sentinel state via env.
    OPTIONAL="$OPTIONAL" python3 <<'PY'
import json, os
# Keep OPTIONAL_PLUGINS in sync with OPTIONAL_SKILLS in sync-to-ides.py.
OPTIONAL_PLUGINS = frozenset({'obsidian-skills', 'argos-cli', 'argos-pr-review'})
optional = os.environ['OPTIONAL'] == '1'
plugins = json.load(open('plugins.json'))['plugins']
selected = plugins if optional else [p for p in plugins if p['name'] not in OPTIONAL_PLUGINS]
print(f"Found {len(selected)} item(s) for mode {'optional' if optional else 'default'!r}:")
print()
for p in selected:
    print(f"  - {p['name']}: {p['description']}")
    print(f"      $ {p['install']}")
PY
    echo ""
    read -p "Install external skills/plugins? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Install strings come from JSON; parse with shlex, allowlist `npx skills`,
        # run with argv (no shell). Per-plugin failures are non-fatal.
        OPTIONAL="$OPTIONAL" python3 <<'PY'
import json, os, shlex, subprocess, sys
OPTIONAL_PLUGINS = frozenset({'obsidian-skills', 'argos-cli', 'argos-pr-review'})
optional = os.environ['OPTIONAL'] == '1'
plugins = json.load(open('plugins.json'))['plugins']

for p in plugins:
    name, install = p['name'], p['install']
    if not optional and name in OPTIONAL_PLUGINS:
        print(f"  · Skipping {name} (optional, no sentinel)", file=sys.stderr)
        continue
    try:
        argv = shlex.split(install)
    except ValueError as e:
        print(f"  ✗ {name} skipped: cannot parse ({e})", file=sys.stderr)
        continue
    if argv[:2] != ['npx', 'skills']:
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
echo "Re-run \`python3 sync-to-ides.py\` any time to re-sync (or after toggling"
echo "the ~/.claude/optional sentinel)."
