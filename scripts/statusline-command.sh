#!/bin/sh
input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
dir=$(basename "$cwd")

branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)

if [ -n "$branch" ]; then
  printf "%s on %s" "$dir" "$branch"
else
  printf "%s" "$dir"
fi
