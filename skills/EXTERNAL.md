# Vendored external skills

Skills listed here are copied from upstream repos rather than authored here.
Keep the upstream SHA recorded so we can diff against it before re-vendoring.

## How to update

```bash
cd /tmp
rm -rf argos-upstream
git clone --depth=1 --filter=tree:0 --sparse https://github.com/argos-ci/argos-javascript.git argos-upstream
cd argos-upstream && git sparse-checkout set skills
cp -r skills/argos-cli skills/argos-pr-review ~/projects/agent-config/skills/
# then update the SHA below + commit
```

If upstream adds or renames a skill, re-vendor it and update this list.

## Vendored skills

| Skill | Source | Commit SHA | Last updated |
|---|---|---|---|
| `argos-cli` | [argos-ci/argos-javascript](https://github.com/argos-ci/argos-javascript/tree/main/skills/argos-cli) | `906c65c` | 2026-04-18 |
| `argos-pr-review` | [argos-ci/argos-javascript](https://github.com/argos-ci/argos-javascript/tree/main/skills/argos-pr-review) | `906c65c` | 2026-04-18 |

## Why vendor instead of `npx skills add`

- Source of truth stays in this repo — a fresh machine clone + `sync-to-ides.py` is enough, no extra install step.
- `skills` CLI has no manifest file, so symlink installs it creates aren't reproducible on a new machine without re-running every `npx skills add` command from memory.
- Vendoring also pins the exact upstream SHA so upstream changes don't silently alter behavior.
