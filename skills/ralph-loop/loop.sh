#!/bin/bash
# Ralph Loop — fresh-context-per-iteration autonomous development
#
# Usage:
#   ./loop.sh              # Build mode, unlimited iterations
#   ./loop.sh 20           # Build mode, max 20 iterations
#   ./loop.sh plan         # Plan mode, unlimited iterations
#   ./loop.sh plan 5       # Plan mode, max 5 iterations
#   ./loop.sh build 30     # Build mode (explicit), max 30 iterations
#
# Based on Geoffrey Huntley's Ralph Wiggum technique.
# Each iteration spawns a fresh Claude context — memory persists
# only through the filesystem (IMPLEMENTATION_PLAN.md, specs/, git).

set -euo pipefail

ITERATION=0
LOOP_START=$(date +%s)
CLAUDE_PID=""

# Format seconds as "Xm Ys"
fmt_duration() { echo "$(( $1 / 60 ))m $(( $1 % 60 ))s"; }

# Print summary box — used by both cleanup and normal exit
print_summary() {
    local status="$1"
    local now=$(date +%s)
    local total_elapsed=$(( now - LOOP_START ))
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Ralph Loop $status"
    echo "  Mode:       $MODE"
    echo "  Iterations: $ITERATION"
    echo "  Total time: $(fmt_duration $total_elapsed)"
    echo "  Branch:     $CURRENT_BRANCH"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Ctrl+C kills the whole script including any running claude process
cleanup() {
    if [ -n "$CLAUDE_PID" ] && kill -0 "$CLAUDE_PID" 2>/dev/null; then
        kill "$CLAUDE_PID" 2>/dev/null
        wait "$CLAUDE_PID" 2>/dev/null
    fi
    print_summary "interrupted"
    exit 0
}
trap cleanup INT TERM

# Parse arguments
MODE="build"
PROMPT_FILE="PROMPT_build.md"
MAX_ITERATIONS=0

case "${1:-}" in
    plan)
        MODE="plan"
        PROMPT_FILE="PROMPT_plan.md"
        MAX_ITERATIONS=${2:-0}
        ;;
    [0-9]*)
        MAX_ITERATIONS=$1
        ;;
esac

CURRENT_BRANCH=$(git branch --show-current)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Ralph Loop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Mode:   $MODE"
echo "  Prompt: $PROMPT_FILE"
echo "  Branch: $CURRENT_BRANCH"
[ "$MAX_ITERATIONS" -gt 0 ] && echo "  Max:    $MAX_ITERATIONS iterations"
echo "  Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Find prompt file — check current dir, then ralph/ subfolder
if [ -f "$PROMPT_FILE" ]; then
    : # found in current dir
elif [ -f "ralph/$PROMPT_FILE" ]; then
    PROMPT_FILE="ralph/$PROMPT_FILE"
else
    echo "Error: $PROMPT_FILE not found in $(pwd) or ralph/"
    echo ""
    echo "Expected files (in project root or ralph/ folder):"
    echo "  PROMPT_plan.md   — planning mode prompt"
    echo "  PROMPT_build.md  — building mode prompt"
    echo "  specs/           — project specifications"
    echo "  AGENTS.md        — build/run/test commands"
    echo ""
    echo "Run the ralph-loop skill to scaffold these files."
    exit 1
fi

# Verify specs exist
if [ ! -d "specs" ] || [ -z "$(ls -A specs/ 2>/dev/null)" ]; then
    echo "Warning: specs/ directory is empty or missing"
    echo "Ralph works best with detailed specs. Continue anyway? (y/N)"
    read -r -n 1 REPLY
    echo ""
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

while true; do
    if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$ITERATION" -ge "$MAX_ITERATIONS" ]; then
        echo ""
        echo "━━━ Reached max iterations: $MAX_ITERATIONS ━━━"
        break
    fi

    ITER_START=$(date +%s)
    echo ""
    echo "━━━ Iteration $((ITERATION + 1)) ($MODE mode) ━━━"
    echo "    Started: $(date '+%H:%M:%S')"
    echo ""

    # Run Ralph iteration with fresh context in background so trap can kill it
    claude -p \
        --dangerously-skip-permissions \
        --model opus \
        --verbose < "$PROMPT_FILE" &
    CLAUDE_PID=$!
    wait "$CLAUDE_PID"
    CLAUDE_PID=""

    ITERATION=$((ITERATION + 1))
    local_now=$(date +%s)
    iter_elapsed=$(( local_now - ITER_START ))
    total_elapsed=$(( local_now - LOOP_START ))
    avg_elapsed=$(( total_elapsed / ITERATION ))

    echo ""
    echo "━━━ Completed iteration $ITERATION ━━━"
    echo "    Duration:   $(fmt_duration $iter_elapsed)"
    echo "    Avg iter:   $(fmt_duration $avg_elapsed)"
    echo "    Total time: $(fmt_duration $total_elapsed)"
    if [ "$MAX_ITERATIONS" -gt 0 ]; then
        remaining=$(( MAX_ITERATIONS - ITERATION ))
        eta_secs=$(( avg_elapsed * remaining ))
        eta_time=$(date -v+"${eta_secs}S" '+%H:%M:%S' 2>/dev/null || date -d "+${eta_secs} seconds" '+%H:%M:%S' 2>/dev/null || echo "unknown")
        echo "    Remaining:  $remaining iterations (~$(fmt_duration $eta_secs), ETA $eta_time)"
    fi
done

print_summary "complete"
