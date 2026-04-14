#!/usr/bin/env python3
"""Analyze decision logs for repeated tool patterns that should become skills.

Reads JSONL decision logs, finds recurring tool sequences, and reports
candidates for skill creation.

Usage:
    python3 analyze-patterns.py [--days 7] [--min-occurrences 3] [--json]
"""

import json
import sys
import os
import glob
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

def parse_args():
    days = 7
    min_occ = 3
    output_json = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--days" and i + 1 < len(args):
            days = int(args[i + 1]); i += 2
        elif args[i] == "--min-occurrences" and i + 1 < len(args):
            min_occ = int(args[i + 1]); i += 2
        elif args[i] == "--json":
            output_json = True; i += 1
        else:
            i += 1
    return days, min_occ, output_json

def load_logs(days):
    log_dir = Path.home() / ".claude" / "logs"
    entries = []
    cutoff = datetime.now() - timedelta(days=days)

    for f in sorted(glob.glob(str(log_dir / "decisions-*.jsonl"))):
        # Parse date from filename
        fname = os.path.basename(f)
        try:
            date_str = fname.replace("decisions-", "").replace(".jsonl", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                continue
        except ValueError:
            continue

        with open(f, errors="replace") as fh:
            for line in fh:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("tool"):
                        entries.append(entry)
                except (json.JSONDecodeError, KeyError):
                    continue
    return entries

def extract_sequences(entries, window=3):
    """Group entries by session, extract tool sequences of length `window`."""
    by_session = defaultdict(list)
    for e in entries:
        sid = e.get("session", "unknown")
        by_session[sid].append(e)

    sequences = Counter()
    for sid, session_entries in by_session.items():
        tools = [e["tool"] for e in session_entries]
        for i in range(len(tools) - window + 1):
            seq = tuple(tools[i:i + window])
            # Skip boring sequences (all same tool, or all TaskUpdate/TaskCreate)
            if len(set(seq)) == 1:
                continue
            if all(t.startswith("Task") for t in seq):
                continue
            sequences[seq] += 1

    return sequences

def extract_tool_frequencies(entries):
    """Count tool usage frequency."""
    return Counter(e["tool"] for e in entries)

def extract_bash_commands(entries):
    """Find repeated Bash commands."""
    commands = Counter()
    for e in entries:
        if e.get("tool") == "Bash":
            cmd = e.get("input", {}).get("command", "")
            # Normalize: strip variable values, keep structure
            if cmd and len(cmd) < 200:
                commands[cmd] += 1
    return commands

def extract_session_stats(entries):
    """Per-session statistics."""
    by_session = defaultdict(list)
    for e in entries:
        by_session[e.get("session", "unknown")].append(e)

    stats = []
    for sid, session_entries in by_session.items():
        tools = Counter(e["tool"] for e in session_entries)
        stats.append({
            "session": sid[:8],
            "tool_count": len(session_entries),
            "unique_tools": len(tools),
            "top_tools": tools.most_common(5),
            "bash_count": tools.get("Bash", 0),
        })
    return sorted(stats, key=lambda x: x["tool_count"], reverse=True)

def find_skill_candidates(sequences, bash_commands, min_occ):
    """Identify patterns that should become skills."""
    candidates = []

    # Tool sequences that repeat across sessions
    for seq, count in sequences.most_common(20):
        if count >= min_occ:
            candidates.append({
                "type": "tool_sequence",
                "pattern": " -> ".join(seq),
                "occurrences": count,
                "suggestion": f"Repeated {len(seq)}-step sequence appearing {count} times. Consider bundling into a skill."
            })

    # Bash commands that repeat
    for cmd, count in bash_commands.most_common(20):
        if count >= min_occ and not cmd.startswith("git ") and not cmd.startswith("ls "):
            candidates.append({
                "type": "bash_command",
                "pattern": cmd[:100],
                "occurrences": count,
                "suggestion": f"Bash command repeated {count} times. Consider wrapping in a skill or alias."
            })

    return candidates

def main():
    days, min_occ, output_json = parse_args()
    entries = load_logs(days)

    if not entries:
        print(f"No decision log entries found for the last {days} days.")
        sys.exit(0)

    sequences = extract_sequences(entries)
    tool_freq = extract_tool_frequencies(entries)
    bash_cmds = extract_bash_commands(entries)
    session_stats = extract_session_stats(entries)
    candidates = find_skill_candidates(sequences, bash_cmds, min_occ)

    result = {
        "period_days": days,
        "total_entries": len(entries),
        "total_sessions": len(session_stats),
        "tool_frequency": dict(tool_freq.most_common(20)),
        "session_stats": session_stats[:10],
        "skill_candidates": candidates,
        "top_sequences": [{"pattern": " -> ".join(s), "count": c} for s, c in sequences.most_common(10)],
        "repeated_bash": [{"command": cmd[:100], "count": c} for cmd, c in bash_cmds.most_common(10) if c >= 2],
    }

    if output_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n=== Decision Log Analysis ({days} days) ===")
        print(f"Entries: {len(entries)} across {len(session_stats)} sessions\n")

        print("Top tools:")
        for tool, count in tool_freq.most_common(10):
            print(f"  {tool:30s} {count:>5}")

        print(f"\nSessions (by activity):")
        for s in session_stats[:5]:
            print(f"  {s['session']}  {s['tool_count']} calls  ({s['bash_count']} Bash)")

        if candidates:
            print(f"\n=== Skill Candidates ({len(candidates)} found) ===")
            for c in candidates:
                print(f"\n  [{c['type']}] {c['pattern']}")
                print(f"  Occurrences: {c['occurrences']}")
                print(f"  -> {c['suggestion']}")
        else:
            print(f"\nNo patterns met the threshold ({min_occ}+ occurrences).")

        if result["top_sequences"]:
            print(f"\nTop tool sequences (3-step):")
            for s in result["top_sequences"][:5]:
                print(f"  {s['pattern']:60s} x{s['count']}")

if __name__ == "__main__":
    main()
