#!/usr/bin/env bash
# Install external skills listed in external-skills.json into ~/.claude/skills/.
# Uses `npx skills add -g` — always fetches latest from source, no vendoring.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_DIR/external-skills.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "No manifest at $MANIFEST" >&2
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found — install Node.js to continue" >&2
  exit 1
fi

# Parse with python (always available on macOS) to avoid a jq dependency.
python3 - "$MANIFEST" <<'PY' | while IFS=$'\t' read -r source skills; do
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
for entry in data.get("skills", []):
    print(entry["source"] + "\t" + " ".join(entry["skills"]))
PY
  echo
  echo "→ $source (${skills})"
  skill_flags=()
  for s in $skills; do
    skill_flags+=(-s "$s")
  done
  npx --yes skills@1.5.1 add "$source" -g -a claude-code "${skill_flags[@]}" -y
done
