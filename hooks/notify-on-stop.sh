#!/bin/bash
# Hook: Stop event notifier
# Auto-generates notification context from decision logs + git state.
# Falls back gracefully if stop-context.json exists (uses it as override).

INPUT=$(cat)
STOP_REASON=$(echo "$INPUT" | jq -r '.stop_reason // "completed"' 2>/dev/null)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null)
SHORT_SESSION="${SESSION_ID:0:8}"
PROJECT=$(basename "${CLAUDE_PROJECT_DIR:-$(pwd)}")

# Never notify when user manually stopped
case "$STOP_REASON" in
  stopped_by_user) exit 0 ;;
esac

CONTEXT_FILE="$HOME/.claude/stop-context.json"

if [ -f "$CONTEXT_FILE" ]; then
  # Claude wrote explicit context — use it (highest fidelity)
  CONVO=$(jq -r '.conversation // "unnamed"' "$CONTEXT_FILE" 2>/dev/null)
  TASK=$(jq -r '.task // "unknown"' "$CONTEXT_FILE" 2>/dev/null)
  PROGRESS=$(jq -r '.progress // ""' "$CONTEXT_FILE" 2>/dev/null)
  REASON=$(jq -r '.reason // ""' "$CONTEXT_FILE" 2>/dev/null)
  QUESTIONS=$(jq -r '.questions // ""' "$CONTEXT_FILE" 2>/dev/null)
  STATUS=$(jq -r '.status // "done"' "$CONTEXT_FILE" 2>/dev/null)
  rm -f "$CONTEXT_FILE"
else
  # Auto-generate context from environment signals
  STATUS="done"
  QUESTIONS=""

  # Conversation name: use git branch or project name
  BRANCH=$(git -C "$(pwd)" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  CONVO="${BRANCH:-$PROJECT}"

  # Task: derive from recent git commits (last 30 min)
  RECENT_COMMITS=$(git -C "$(pwd)" log --oneline --since="30 minutes ago" 2>/dev/null | head -5)
  if [ -n "$RECENT_COMMITS" ]; then
    TASK=$(echo "$RECENT_COMMITS" | head -1 | cut -c9-)
  else
    TASK="Session in $PROJECT"
  fi

  # Progress: summarize from recent commits + git status
  COMMIT_COUNT=$(echo "$RECENT_COMMITS" | grep -c . 2>/dev/null || echo "0")
  UNCOMMITTED=$(git -C "$(pwd)" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  PROGRESS=""
  if [ "$COMMIT_COUNT" -gt 0 ]; then
    PROGRESS="- $COMMIT_COUNT commit(s) this session"
    PROGRESS="$PROGRESS
$(echo "$RECENT_COMMITS" | sed 's/^/- /')"
  fi
  if [ "$UNCOMMITTED" -gt 0 ]; then
    PROGRESS="$PROGRESS
- $UNCOMMITTED uncommitted file(s)"
  fi

  # Reason: derive from stop reason
  case "$STOP_REASON" in
    end_turn) REASON="Completed response" ;;
    max_tokens) REASON="Hit context limit" ;;
    tool_error) REASON="Tool error"; STATUS="blocked" ;;
    *) REASON="$STOP_REASON" ;;
  esac

  # Check decision logs for session activity (last 30 min)
  LOG_FILE="$HOME/.claude/logs/decisions-$(date +%Y-%m-%d).jsonl"
  if [ -f "$LOG_FILE" ]; then
    TOOL_COUNT=$(tail -200 "$LOG_FILE" | wc -l | tr -d ' ')
    if [ -z "$PROGRESS" ]; then
      PROGRESS="- $TOOL_COUNT tool calls in recent log"
    fi
  fi
fi

# Skip if nothing meaningful to report
if [ -z "$PROGRESS" ] && [ -z "$TASK" ]; then
  exit 0
fi

# Determine type
if [ "$STATUS" = "blocked" ] || { [ -n "$QUESTIONS" ] && [ "$QUESTIONS" != "" ]; }; then
  EMOJI=$'\xE2\x9A\xA0\xEF\xB8\x8F'
  TITLE="Needs Input"
else
  EMOJI=$'\xE2\x9C\x85'
  TITLE="Done"
fi

# Build message
TEXT="——————————————
*Convo:* ${CONVO}
*Status:* ${EMOJI} ${TITLE}
*Project:* ${PROJECT}"

if [ -n "$PROGRESS" ] && [ "$PROGRESS" != "" ]; then
  TEXT="${TEXT}

*Progress:*
${PROGRESS}"
fi

if [ -n "$REASON" ] && [ "$REASON" != "" ]; then
  TEXT="${TEXT}

*Reason:* ${REASON}"
fi

if [ -n "$QUESTIONS" ] && [ "$QUESTIONS" != "" ]; then
  TEXT="${TEXT}

*Blocker:*
${QUESTIONS}"
fi

# Dedup: skip if identical message was just sent
HASH_FILE="$HOME/.claude/.last-notify-hash"
MSG_HASH=$(echo "$TEXT" | md5 2>/dev/null || echo "$TEXT" | md5sum 2>/dev/null | cut -d' ' -f1)
if [ -f "$HASH_FILE" ] && [ "$(cat "$HASH_FILE")" = "$MSG_HASH" ]; then
  exit 0
fi
echo "$MSG_HASH" > "$HASH_FILE"

# Telegram notification
if [ -f "$HOME/.claude/telegram.env" ]; then
  source "$HOME/.claude/telegram.env"
  if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      --data-urlencode "text=${TEXT}" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "parse_mode=Markdown" > /dev/null 2>&1
  fi
fi

# Auto-save session summary to Obsidian (if vault exists)
OBSIDIAN_VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Claude"
DAILY_NOTE="$OBSIDIAN_VAULT/Daily/$(date +%Y-%m-%d).md"
if [ -d "$OBSIDIAN_VAULT" ]; then
  mkdir -p "$OBSIDIAN_VAULT/Daily"
  echo "" >> "$DAILY_NOTE"
  echo "## $(date +%H:%M) — ${CONVO}" >> "$DAILY_NOTE"
  echo "**Project:** ${PROJECT} | **Status:** ${STATUS}" >> "$DAILY_NOTE"
  [ -n "$TASK" ] && echo "**Task:** ${TASK}" >> "$DAILY_NOTE"
  [ -n "$PROGRESS" ] && echo "$PROGRESS" >> "$DAILY_NOTE"
fi

exit 0
