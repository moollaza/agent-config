---
name: autonomy-bootstrap
description: Set up Claude Code for autonomous operation on a new machine or for a new user. Installs the operating contract (CLAUDE.md), hooks (question friction gate, decision logger, Telegram notifier), and Telegram bot configuration. Use when setting up a new machine, onboarding a teammate, or when the user says "set up autonomy", "bootstrap", "configure Claude for autonomous mode", "set up hooks", or "make Claude more autonomous". Also use when the user's hooks or CLAUDE.md seem missing or misconfigured.
---

# Autonomy Bootstrap

Set up Claude Code for fully autonomous operation with Telegram notifications.

## What gets installed

1. **`~/.claude/CLAUDE.md`** — Operating contract with 4-tier decision framework
2. **`~/.claude/hooks/ask-user-friction.sh`** — Blocks reflexive questions, forces structured asks
3. **`~/.claude/hooks/log-decisions.sh`** — Async decision logger for review
4. **`~/.claude/hooks/notify-on-stop.sh`** — Telegram notifications on task complete/blocked
5. **`~/.claude/settings.json`** — Hook wiring + permissions
6. **`~/.claude/telegram.env`** — Bot credentials (if setting up Telegram)

## Step 1: Check current state

```bash
echo "=== CLAUDE.md ===" && (head -3 ~/.claude/CLAUDE.md 2>/dev/null || echo "MISSING")
echo "=== Hooks ===" && ls ~/.claude/hooks/ 2>/dev/null || echo "MISSING"
echo "=== Settings hooks ===" && (jq '.hooks | keys' ~/.claude/settings.json 2>/dev/null || echo "NO HOOKS")
echo "=== Telegram ===" && (test -f ~/.claude/telegram.env && echo "CONFIGURED" || echo "NOT SET UP")
```

Report what exists and what's missing.

## Step 2: Install from agent-config repo

The source of truth is the `agent-config` repo. Pull the latest:

```bash
cd ~/projects/agent-config && git pull origin main
```

### Install CLAUDE.md

Copy the operating contract. **Do not overwrite** if one exists — diff first and ask the user.

```bash
diff ~/.claude/CLAUDE.md ~/projects/agent-config/docs/templates/CLAUDE.md 2>/dev/null || echo "No existing file, safe to install"
```

### Install hooks

```bash
mkdir -p ~/.claude/hooks
cp ~/projects/agent-config/docs/templates/hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh
```

### Wire hooks in settings.json

Read the current `~/.claude/settings.json`, merge in the hook configuration:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "AskUserQuestion",
        "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/ask-user-friction.sh", "timeout": 5}]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/log-decisions.sh", "timeout": 5, "async": true}]
      }
    ],
    "Stop": [
      {
        "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/notify-on-stop.sh", "timeout": 10}]
      }
    ]
  }
}
```

**Merge carefully** — don't overwrite existing settings. Use `jq` to merge hooks into the existing file.

## Step 3: Set up Telegram (if not configured)

If `~/.claude/telegram.env` doesn't exist:

1. Tell the user to message [@BotFather](https://t.me/BotFather) on Telegram and create a bot
2. Ask for the bot token
3. Fetch the chat ID:

```bash
curl -s "https://api.telegram.org/bot${TOKEN}/getUpdates" | jq '.result[0].message.chat.id'
```

4. Write the env file:

```bash
cat > ~/.claude/telegram.env << EOF
TELEGRAM_BOT_TOKEN=${TOKEN}
TELEGRAM_CHAT_ID=${CHAT_ID}
EOF
chmod 600 ~/.claude/telegram.env
```

5. Send a test message to verify.

## Step 4: Verify

Run a full check:

```bash
echo "=== Hooks executable ===" && ls -la ~/.claude/hooks/*.sh
echo "=== Settings hooks ===" && jq '.hooks | keys' ~/.claude/settings.json
echo "=== Telegram test ===" && source ~/.claude/telegram.env && curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" --data-urlencode "text=✅ Autonomy bootstrap complete" -d "chat_id=${TELEGRAM_CHAT_ID}" -d "parse_mode=Markdown" | jq '.ok'
```

## Step 5: Report

Output what was installed, what was skipped, and any manual steps remaining.
