#!/bin/bash
# SessionStart hook: load service registry context and check credential health
# Outputs context that gets injected into the conversation

REGISTRY="$HOME/.claude/service-registry.json"

# Load service registry summary
if [ -f "$REGISTRY" ]; then
  PROJECT_COUNT=$(jq '.projects | length' "$REGISTRY" 2>/dev/null)
  PROJECT_NAMES=$(jq -r '.projects | keys | join(", ")' "$REGISTRY" 2>/dev/null)
  echo "Service registry loaded: $PROJECT_COUNT projects ($PROJECT_NAMES)"
  echo "Use ~/.claude/service-registry.json to resolve project service IDs without discovery API calls."
fi

# Quick credential health check
CRED_STATUS=""

# Fathom
if [ -n "$FATHOM_API_KEY" ] || security find-generic-password -s "fathom-api-key" -w >/dev/null 2>&1; then
  CRED_STATUS="$CRED_STATUS Fathom:OK"
else
  CRED_STATUS="$CRED_STATUS Fathom:MISSING"
fi

# Cloudflare
if [ -n "$CLOUDFLARE_API_TOKEN" ] || [ -n "$CF_API_TOKEN" ] || security find-generic-password -s "cloudflare-api-token" -w >/dev/null 2>&1; then
  CRED_STATUS="$CRED_STATUS Cloudflare:OK"
else
  CRED_STATUS="$CRED_STATUS Cloudflare:MISSING"
fi

# Sentry
if [ -n "$SENTRY_AUTH_TOKEN" ] || security find-generic-password -s "sentry-auth-token" -w >/dev/null 2>&1; then
  CRED_STATUS="$CRED_STATUS Sentry:OK"
else
  CRED_STATUS="$CRED_STATUS Sentry:MISSING"
fi

# GSC
if [ -f "$HOME/.config/gsc/credentials.json" ]; then
  CRED_STATUS="$CRED_STATUS GSC:OK"
else
  CRED_STATUS="$CRED_STATUS GSC:MISSING"
fi

echo "Credentials:$CRED_STATUS"

# Load Obsidian project context if working in a known project
CWD=$(pwd)
PROJECT_DIR=$(basename "$CWD")

OBSIDIAN_VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude"
PROJECT_NOTE="$OBSIDIAN_VAULT/Projects/$PROJECT_DIR.md"

if [ -f "$PROJECT_NOTE" ]; then
  echo ""
  echo "=== Obsidian project context for $PROJECT_DIR ==="
  head -50 "$PROJECT_NOTE"
  echo "=== end project context ==="
fi
