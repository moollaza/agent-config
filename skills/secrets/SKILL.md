---
name: secrets
description: >
  Find, reference, and use project credentials stored in macOS Keychain via
  the `secret` wrapper. Use when handling API keys, OAuth credentials,
  Cloudflare/Worker secrets, or any token-bearing call. Triggers on "secret",
  "API key", "credential", "Keychain", "wrangler secret", "rotate token",
  ".dev.vars". 1Password is no longer in the CLI path.
---

# secrets

Zaahir's CLI-accessible project secrets live in **macOS Keychain**, accessed through the `secret` wrapper at `~/.local/bin/secret`. The login keychain auto-unlocks at login, so reads from agents and subshells produce **zero Touch ID prompts** in normal use.

Context: This replaced 1Password for the CLI path on 2026-05-11. 1Password's biometric-only mode prompts Touch ID per `op` invocation — parallel agent reads of three different secrets produced three prompts every time, with no session-token escape hatch. Tracking: [ZPR-75](https://linear.app/moollapps/issue/ZPR-75). 1Password remains for browser fills and mobile; it is not the source of truth for anything an agent or CLI tool consumes.

## The `secret` wrapper

```sh
secret get <name>            # print value to stdout
secret put <name>            # store value (stdin or interactive prompt; never as arg)
secret list                  # list managed names
secret delete <name>         # remove
secret has <name>            # exit 0/1, no output
```

Items are stored as `service=<name>, account=$USER` generic passwords. Managed names are also tracked in `~/.local/share/secrets/registry` so `secret list` returns the curated set rather than your entire keychain.

## Reading values

```sh
# Good — direct pipe, value never lands in a shell variable
secret get fathom-analytics-key | bunx wrangler secret put FATHOM_API_KEY

# Acceptable — single-command export, scoped to one invocation
CLOUDFLARE_API_TOKEN=$(secret get cloudflare-api-token) wrangler whoami

# Bad — value persists in shell env, may leak via subsequent logging
export CLOUDFLARE_API_TOKEN=$(secret get cloudflare-api-token)
```

## Writing / rotating

```sh
# Non-interactive (from stdin) — prefer this in scripts
printf '%s' "$NEW_TOKEN" | secret put cloudflare-api-token

# Interactive — prompts with hidden input
secret put cloudflare-api-token
```

Rotation flow: rotate at provider → `secret put` overwrites in keychain → consumers pick up new value on next read. No file changes needed.

## Naming convention

kebab-case, descriptive, no prefix. Run `secret list` for the current set. Examples in use:

- `cloudflare-api-token` (consolidated Project-Hub-scoped CF token; used by wrangler + OpenTofu)
- `fathom-analytics-key`
- `pagespeed-api-key` (existing — see `~/.zshrc:68`)
- `sentry-pat`
- `supabase-choosetwo-api-secret`
- `plane-api-token`
- `reporemover-dev-token`

## Pushing to Cloudflare Workers

```sh
secret get <name> | bunx wrangler secret put <REMOTE_NAME> --name <worker>
```

For multi-secret apps, use a `.dev.vars.tpl` that lists local secret names (not `op://` refs), processed by a small sync script. See `~/projects/project-hub/bin/sync-worker-secrets` (per ZPR-75 migration follow-up).

## Sandbox detection (Claude Desktop, web/Cowork, container CI)

The `secret` wrapper requires the user's local macOS Keychain. Sandboxed surfaces — Claude Desktop, Claude Code on web/Cowork, sandboxed CI, any container that doesn't mount `$HOME` — **cannot reach it**.

**Pre-check before the first credential-bearing step:**

```sh
[ -x ~/.local/bin/secret ] || echo "SANDBOX: secret wrapper unreachable"
```

If the check trips, do **not**:

- Retry, hope, or fall back to a different store.
- Ask the user to paste the credential into chat. Chat transcripts persist, get screenshotted, and end up in eval datasets. Pasted secrets must be rotated.
- Improvise an alternate flow that skips authentication.

Instead:

1. **Name the exact secret needed** — e.g. "I need `secret get cloudflare-api-token` to push the worker."
2. **Offer two paths**: (a) the user elevates permissions / mounts `$HOME` and you rerun, or (b) the user runs the gated step locally and reports back the result (status code, output without the token).
3. **If neither is feasible, mark the work as blocked.** Better a clear stop than a half-deployed worker with a bad token.

## Hard rules

- **Never** echo a resolved secret value, even for "diagnostics." Verify with `[ -n "$VAL" ] && echo "len=${#VAL}"` or `secret get x | wc -c`.
- **Never** write secret values to disk except as committed `.dev.vars.tpl`-style templates pointing at keychain names — never values.
- **Never** assign to an env var with `export` that persists beyond the immediate command, unless intentional and scoped.
- **Never** add CLI-callable items to 1Password going forward. If a tool needs an env var, it goes in keychain.
- During `secret put`, the value is briefly visible in the process listing (macOS `security` CLI limitation). Single-user laptop only.

## Migrating an item from 1Password

For one-off needs during the ZPR-75 migration:

```sh
op read 'op://Developer/<title>/password' | secret put <kebab-case-name>
```

One Touch ID prompt per item. Once migrated, remove the `op://` reference from any templates.
