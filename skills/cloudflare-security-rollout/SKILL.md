---
name: cloudflare-security-rollout
description: Audit and roll out Cloudflare security baselines for project-hub managed domains. Use when working on Cloudflare Security Insights, OpenTofu changes under infra/cloudflare, www-to-apex redirects, TLS/HSTS/WAF/Bot Fight Mode decisions, R2 OpenTofu state, or updating project-hub Cloudflare inventory and standards.
---

# Cloudflare Security Rollout

## Workflow

1. Read `standards/cloudflare-security.md`, `standards/cloudflare-account.md`, and `infra/cloudflare/README.md`.
2. Use the Cloudflare skill/plugin docs for current API/provider behavior before changing resources.
3. Run read-only audit and smoke scripts before proposing the next stage.
4. For live changes, use OpenTofu from `infra/cloudflare`; avoid dashboard-only changes unless the docs say a one-time dashboard activation is required.
5. Run `tofu plan` and confirm it has no unexpected destroys before applying.
6. After apply, run `tofu plan`, `scripts/smoke-www-redirects.sh`, and relevant apex/app smoke checks.
7. Update `TODO.md`, `inventory.md`, `standards/cloudflare-account.md`, `standards/cloudflare-security.md`, and Cloudflare plan/audit docs.

## Decisions

- Keep apex as canonical; redirect `www` to apex.
- Keep HSTS staged: 6 months, `nosniff=true`, no preload, no includeSubDomains until subdomains are verified.
- Keep Bot Fight Mode and AI crawler controls as per-domain opt-ins, not fleet defaults.
- Do not treat Security Center insights as the only source of truth immediately after an apply; verify live zone settings and note stale insights.
- Do not enable HSTS on a zone whose apex HTTPS smoke test fails.

## Commands

See `references/commands.md` for repeatable commands and token handling.
