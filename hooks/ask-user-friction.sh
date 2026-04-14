#!/bin/bash
# Hook: PreToolUse gate on AskUserQuestion
# Purpose: Block reflexive questions, force Claude to try harder before asking.
# Exit 0 = allow, Exit 2 = block (stderr shown to Claude as feedback)

INPUT=$(cat)
QUESTION=$(echo "$INPUT" | jq -r '.tool_input.question // empty' 2>/dev/null)

if [ -z "$QUESTION" ]; then
  exit 0
fi

# Block reflexive "should I continue?" style questions
if echo "$QUESTION" | grep -iqE "^(should I|shall I|do you want|is (this|that) (ok|okay|fine|correct|right)|can I proceed|ready to|want me to|continue\?|go ahead)"; then
  cat >&2 <<'EOF'
BLOCKED: Reflexive question detected. You are an autonomous agent.

Before asking the user anything:
1. Re-read the task requirements
2. Make a decision using the Decision-Making Framework (Tier 1-3 = proceed without asking)
3. Only ask if this is genuinely Tier 4 (destructive, irreversible, security-sensitive, or missing credentials)

If you must ask, provide:
- What you're blocked on (specific)
- 2-3 concrete options with your recommended default
- Why you can't just pick the default yourself
EOF
  exit 2
fi

# Block vague open-ended questions
WORD_COUNT=$(echo "$QUESTION" | wc -w | tr -d ' ')
if [ "$WORD_COUNT" -lt 5 ] && echo "$QUESTION" | grep -iqE "\?$"; then
  cat >&2 <<'EOF'
BLOCKED: Question too vague. If you must ask the user something, be specific:
- State what you've tried
- Provide 2-3 options with a recommended default
- Explain why this is a Tier 4 decision you can't make yourself
EOF
  exit 2
fi

exit 0
