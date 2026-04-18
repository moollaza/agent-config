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
    echo "Installing external skills from external-skills.json..."
    ./scripts/install-external-skills.sh
    echo ""
    echo "Setup complete!"
    echo ""
    echo "To verify symlinks:"
    echo "  python3 sync-to-ides.py --verify"
else
    echo "Setup cancelled."
    exit 1
fi

