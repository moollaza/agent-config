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

# Install external plugins from plugins.json
echo ""
echo "External plugins"
echo "======================================"
if [ -f "$SCRIPT_DIR/plugins.json" ]; then
    PLUGIN_COUNT=$(python3 -c "import json; print(len(json.load(open('$SCRIPT_DIR/plugins.json'))['plugins']))")
    echo "Found $PLUGIN_COUNT plugin(s) in plugins.json:"
    python3 -c "
import json
plugins = json.load(open('$SCRIPT_DIR/plugins.json'))['plugins']
for p in plugins:
    print(f\"  - {p['name']}: {p['description']}\")
"
    echo ""
    read -p "Install external plugins? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -c "
import json, subprocess, sys
plugins = json.load(open('$SCRIPT_DIR/plugins.json'))['plugins']
for p in plugins:
    print(f\"Installing {p['name']}...\")
    result = subprocess.run(p['install'], shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f\"  ✓ {p['name']} installed\")
    else:
        print(f\"  ✗ {p['name']} failed: {result.stderr.strip()}\", file=sys.stderr)
"
    else
        echo "Plugin install skipped."
    fi
else
    echo "No plugins.json found, skipping."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To verify symlinks:"
echo "  python3 sync-to-ides.py --verify"

