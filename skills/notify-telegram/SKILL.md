---
name: notify-telegram
description: Send a Telegram message to the user from any conversation. Use when Claude needs to notify the user about something — task completion, a question, a status update, or any async communication. Triggers on "notify me", "send me a message", "ping me", "telegram", "let me know when", "text me", or when Claude autonomously decides the user should know something (e.g. long build finished, tests passed/failed, deploy complete). Also use proactively when completing a significant milestone the user would want to know about.
---

# Notify via Telegram

Send a message to the user's Telegram via their personal bot.

## How to send

```bash
source ~/.claude/telegram.env
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "text=YOUR_MESSAGE_HERE" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "parse_mode=Markdown" > /dev/null 2>&1
```

## Message format

Use Telegram Markdown formatting:

```
*Bold* for headers/labels
_Italic_ for project names
`code` for inline code
```

### For status updates:

```
——————————————
*Convo:* short-conversation-name
*Status:* ✅ Done | ⚠️ Blocked | 🔄 In Progress
*Project:* project-name

*Progress:*
- Done: thing 1
- Done: thing 2
- Remaining: thing 3

*Reason:* Why you're sending this

*Blocker:* (only if blocked)
- Specific question or blocker
```

### For quick pings:

```
🔔 *project-name*: Tests passed, PR ready for review
```

## When to use proactively

- Long-running task completed (build, deploy, test suite)
- Significant milestone reached
- Blocked on user input (Tier 4 decision)
- Error that needs human attention
- PR created and ready for review

## Prerequisites

Requires `~/.claude/telegram.env` with `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
If the file doesn't exist, tell the user to set up a Telegram bot first.
