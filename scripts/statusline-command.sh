#!/bin/sh
input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
dir=$(basename "$cwd")
branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
model=$(echo "$input" | jq -r '.model.display_name // empty')
ctx=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms // empty')

# git status emojis
git_status=""
if [ -n "$branch" ]; then
  dirty=$(git -C "$cwd" --no-optional-locks status --porcelain 2>/dev/null | head -1)
  ahead=$(git -C "$cwd" --no-optional-locks rev-list --count @{u}..HEAD 2>/dev/null)
  behind=$(git -C "$cwd" --no-optional-locks rev-list --count HEAD..@{u} 2>/dev/null)

  if [ -n "$dirty" ]; then
    git_status=" ✏️"
  else
    git_status=" ✅"
  fi
  [ "$ahead" -gt 0 ] 2>/dev/null && git_status="$git_status ⬆$ahead"
  [ "$behind" -gt 0 ] 2>/dev/null && git_status="$git_status ⬇$behind"
fi

# format runtime
runtime=""
if [ -n "$duration_ms" ] && [ "$duration_ms" != "0" ]; then
  total_secs=$((duration_ms / 1000))
  mins=$((total_secs / 60))
  secs=$((total_secs % 60))
  if [ "$mins" -gt 0 ]; then
    runtime="${mins}m${secs}s"
  else
    runtime="${secs}s"
  fi
fi

# build output
out="📁 $dir"
[ -n "$branch" ] && out="$out 🔀 $branch$git_status"
[ -n "$model" ] && out="$out | 🤖 $model"
[ -n "$ctx" ] && out="$out | 📊 ctx ${ctx}%"
[ -n "$runtime" ] && out="$out | ⏱️ $runtime"
if [ -n "$cost" ] && [ "$cost" != "0" ]; then
  out="$out | 💰 \$$(printf '%.2f' "$cost")"
fi

printf "%s" "$out"
