# External skills

Skills from upstream projects. Not authored here, not symlinked — installed
directly into `~/.claude/skills/` via [`npx skills`](https://github.com/vercel-labs/skills).
Re-run any install command to refresh from source.

## Install / refresh

### Argos CI — visual regression PR review

```
npx skills@latest add argos-ci/argos-javascript -g -a claude-code -s argos-cli -s argos-pr-review -y
```

Installs two skills: `argos-cli` (operate the Argos CLI) and `argos-pr-review`
(review visual regression builds on PRs).
Docs: https://argos-ci.com/docs/review-builds-with-ai-agents

## Verify

```
ls ~/.claude/skills/argos-cli/SKILL.md ~/.claude/skills/argos-pr-review/SKILL.md
```

Both files should exist. If missing, re-run the relevant install command.

## Remove

```
rm -rf ~/.claude/skills/<skill-name>
```

Then delete the corresponding section from this file.
