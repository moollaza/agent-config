#!/bin/bash
# Hook: PostToolUse async logger
# Purpose: Log tool calls with timestamps for async decision review.
# Runs async — does not block Claude's execution.

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)
SESSION=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null)

LOG_DIR="$HOME/.claude/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/decisions-$(date +%Y-%m-%d).jsonl"

# Only log meaningful decision tools (skip reads/globs for noise reduction)
case "$TOOL" in
  Read|Glob|Grep|ToolSearch|TaskGet|TaskList)
    exit 0
    ;;
esac

# Truncate large inputs to avoid bloating the log
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}' 2>/dev/null | head -c 500)

echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"session\":\"$SESSION\",\"tool\":\"$TOOL\",\"input\":$TOOL_INPUT}" >> "$LOG_FILE" 2>/dev/null

exit 0
