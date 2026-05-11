# Codex Operating Contract

**Read `~/.codex/CLAUDE.md` first** — that's the universal operating contract (shared with Claude Code via symlinks from `~/projects/agent-config/CLAUDE.md`). This file extends it with Codex-specific tool mappings only.

<!-- BEGIN COMPOUND CODEX TOOL MAP -->
## Compound Codex Tool Mapping (Claude Compatibility)

This section maps Claude Code plugin tool references to Codex behavior. Auto-managed.

- Read: `cat`/`sed` or `rg`
- Write: shell redirection or `apply_patch`
- Edit/MultiEdit: `apply_patch`
- Bash: `shell_command`
- Grep: `rg` (fallback: `grep`)
- Glob: `rg --files` or `find`
- LS: `ls` via `shell_command`
- WebFetch/WebSearch: `curl` or Context7
- AskUserQuestion: numbered list, wait for reply. Multi-select = comma-separated.
- Task/Subagent/Parallel: sequential in main thread; `multi_tool_use.parallel` for tool calls.
- TodoWrite/TodoRead: file-based todos in `todos/`.
- Skill: open referenced `SKILL.md`.
- ExitPlanMode: ignore.
<!-- END COMPOUND CODEX TOOL MAP -->
