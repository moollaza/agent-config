# agents-config

Symlinked source of truth for Claude Code and Codex global config. Edit here, not `~/.claude/` or `~/.codex/`.

## Layout

- `AGENTS.md` — universal rules, symlinked as `~/.claude/CLAUDE.md` + `~/.codex/AGENTS.md`
- `skills/` — local skills, symlinked into `~/.claude/skills/`
- `plugins.json` — external skills installed via `npx skills` (registry only, not stored)
- `optional-context.md` — extra rules, see [Optional](#optional)
- `scripts/`, `setup.sh`, `sync-to-ides.py`

`AGENTS.md` is the [cross-agent standard](https://www.aihero.dev/a-complete-guide-to-agents-md) — keep it lean, every token loads on every request.

## Sync

```bash
python3 sync-to-ides.py --dry-run   # preview
python3 sync-to-ides.py             # apply
python3 sync-to-ides.py --force     # also overwrite real files at targets
./setup.sh                          # interactive wrapper + installs plugins.json
```

Always syncs both IDEs. Refuses to clobber non-symlink files unless `--force`.

## Optional

`touch ~/.claude/optional` to additionally sync:

- `optional-context.md` → `~/.claude/rules/` (auto-loaded by Claude, same path as `lethal-trifecta.md`) — adds rules 8–10 to the contract
- Skills in `OPTIONAL_SKILLS` (`sync-to-ides.py`): `secrets`, `swarm-claim`
- Plugins in `OPTIONAL_PLUGINS` (`setup.sh`): `obsidian-skills`, `argos-cli`, `argos-pr-review`

Remove the sentinel and re-sync to evict.

## Adding skills/plugins

- Local skill: drop a directory under `skills/`, re-sync.
- External skill: add an entry to `plugins.json`, run `./setup.sh`.
