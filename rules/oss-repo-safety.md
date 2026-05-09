# OSS Repo Safety

## When this applies

- Any repo whose GitHub visibility is **public**, or that may be open-sourced later.
- The user maintains several public repos (e.g. `zaahir.ca`). Treat *anything* under those as world-readable forever.
- Authoritative list: `inventory.md` in `~/projects/project-hub/` marks each repo public/private.

## How to detect public

Before doing anything that could become a public artifact (commit, push, issue, PR, comment, branch name, fixture, screenshot):

1. Run `gh repo view --json visibility,nameWithOwner -q .visibility` in the repo. If it returns `PUBLIC`, treat as public.
2. If `gh` is unavailable, check `inventory.md`. If still unsure, assume **public**.
3. Forks of OSS projects count as public even if your fork is private — upstream PRs surface your branch name and commit history.

## Pre-commit / pre-push scan

Walk this checklist for every commit headed to a public repo, before running `git commit`:

- [ ] No personal email, phone, home address, or account IDs anywhere in the diff.
- [ ] No private dashboard URLs (Linear, Asana, internal Slack, internal docs). If a link is unavoidable, mark it `(internal)` and verify it's not a credential-bearing URL.
- [ ] No tokens, API keys, `.env` contents, or local secrets — even commented out.
- [ ] No customer/client names, account IDs, or unredacted user data in fixtures, screenshots, or seed data.
- [ ] No security details that could arm an attacker before the fix has shipped (rate-limit values, auth flow specifics, internal endpoints).
- [ ] Branch name is neutral (no Slack/chat context, no slurs, no codename leak).
- [ ] Commit message is factual and public-safe (no venting, no speculation about people, no private context).
- [ ] No unrelated `gitignore`d-by-default files smuggled in (DS_Store, IDE configs, scratch notes).

## PR descriptions

- Follow `rules/pr-descriptions.md`. The "Public-repo posture" section there is the canonical guide.
- Especially in OSS repos: avoid marketing language, decorative emoji, internal acronyms. Reviewers may be strangers — they need context, not hype.

## Issues and discussions in OSS

- Don't drop a private/internal context dump into a public issue. Translate to public-readable framing before posting.
- For a security report on someone else's OSS repo, follow their `SECURITY.md` (or use a private advisory) before opening a public issue.
- For your own OSS repos, accept reports via private security advisory; don't ask reporters to use public issues.

## Licensing and provenance

- New files in OSS repos: confirm a license header isn't required by the existing convention. If `LICENSE` exists at the root and other files don't carry headers, follow that convention.
- Don't paste large blocks of code from third-party sources (Stack Overflow, other repos) without checking license compatibility.
- AI-generated content is fine, but don't claim authorship for code you didn't review.

## When sensitive info reaches git history

- **Stop.** Do not push.
- Notify the user. This is a Tier 4 decision (irreversible if pushed publicly).
- Options: rewrite local history (`git rebase -i`), force-push if not yet shared, or rotate the secret if already public.
- Never silently force-push to fix a leak — the user must approve.

## Practical defaults the agent should adopt

- When generating fixtures or seed data: use placeholder names (`Test User`, `example@example.com`), not real ones.
- When writing tests that hit external services: stub or use a sandboxed account, never the user's production credentials.
- When suggesting commit messages: scrub for chat context the user didn't ask to publish.
- When opening issues programmatically: write them as if a stranger will read them tomorrow.
