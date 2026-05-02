---
description: "Conventions for writing pull request descriptions. Apply whenever creating or updating a PR body — including after a force-push or revision — in any repository, public or private."
alwaysApply: true
---

# PR Description Conventions

## When this applies

- Creating a new PR.
- Editing the body of an existing PR (including after a force-push, scope change, or review-round revision).
- Drafting a PR description for the user to copy.

## Use the repo's template if it exists

If `.github/PULL_REQUEST_TEMPLATE.md` (or a variant) exists, fill it out. Don't invent your own structure on top of it. Add sections from this rule only when the template is missing something important (e.g. no "How to verify").

If no template exists, use the default structure below.

## Default structure

Sections in this order. Omit a section only when it's genuinely not applicable — not to save keystrokes.

```
## Summary
<1–3 sentences, plain language. What changed, at the highest level.>

## Changes
- <one logical change per bullet>
- <one logical change per bullet>

## Why
- <motivation, linked issue, constraint that forced this>

## How to verify
- <runnable step or command>
- <runnable step or command>

## What to look for
- <review focus area>
- <review focus area>

## Notes
- <risks, follow-ups, breaking changes, flags, anything surprising>
```

`Summary`, `Changes`, and `Why` are required. `How to verify` and `What to look for` are required unless the diff is trivially obvious (typo, comment, single-line config bump) — when in doubt, include them. `Notes` is optional.

## Bullets over prose

- Prose walls get skimmed past. Bullets are reviewable.
- Keep each bullet to ~2 sentences max. Break up longer thoughts into separate bullets.
- Use sub-bullets for detail under a parent bullet, not for padding.

## Testing & review checklists

Two separate sections because they serve different reviewers:

### `## How to verify` — runnable steps

Concrete things a reviewer (or CI) can execute:

- Commands: `bundle exec rspec spec/foo_spec.rb`, `npm run build && open http://localhost:3000/foo`.
- Manual steps: "Sign in as admin, click X, expect Y."
- What you actually ran yourself and its result ("Ran the full suite locally — green").
- **What you did *not* test, explicitly.** Examples: "Did not test the legacy flow behind feature flag `Z`", "Did not exercise the Safari path", "Backfill script was not run against a prod-sized dataset."

Never write "tested" without specifics. "Tested" alone is meaningless and often misleading.

### `## What to look for` — eyeball-level review focus

The "if you only have 60 seconds, look at these" list. Think regressions, edge cases, and anything that wouldn't show up in a green CI run:

- Regressions to watch (touched flows elsewhere in the app).
- Edge cases handled — and ones deliberately not handled (say so).
- UX states to eyeball: loading, empty, error, disabled, mobile.
- Accessibility touchpoints (focus order, aria labels, contrast).
- Performance concerns (new N+1, large list renders, bundle size).
- Config / env-var changes to re-read.
- Schema migrations or data backfills to sanity-check.
- Load-bearing deletions (see "No silent deletions" in CLAUDE.md).

## Transparency defaults — don't be misleading

- Never claim "tested" without specifics. Say what you ran, what you skipped, and why.
- Flag breaking changes on their own line, prefixed `**Breaking:**`. Don't bury them.
- Flag partial rollouts, feature-flag gating, and follow-up work explicitly.
- Enumerate every file/config deletion outside the stated scope with a one-line justification (reinforces the `No silent deletions` rule in CLAUDE.md).
- Surface known limitations and regressions. Don't paper over them — reviewers will find them anyway, and the credibility cost of discovery is higher than the cost of disclosure.

## Public-repo posture — don't embarrass or self-harm

Assume a PR in a public repo will be read by strangers, future maintainers, journalists, and security researchers. Write accordingly:

- No personal email addresses, phone numbers, home addresses, personal account IDs, billing details, or private contact channels. Use product-owned aliases or placeholders.
- No customer names, account IDs, internal URLs, private dashboards, or Slack/Linear/Asana links without an explicit `(internal)` marker.
- No unpatched security detail that could arm an attacker. If disclosure is needed, wait until the mitigation has shipped.
- No marketing hype or self-congratulation. Avoid superlatives ("blazingly fast", "game-changing", "massive improvement"). Use neutral, factual language.
- No decorative emoji in headings or bullets. (Only use emoji when the user explicitly asks.)
- No speculation about other people, teams, competitors, or users.
- Prefer links to public issues and docs. If you must link something internal, mark it `(internal)` so external readers aren't confused.

For private repos the same defaults are still safer — they cost nothing and future-proof against a repo being open-sourced.

## Voice

- Active voice, present or past tense describing what the PR does: "Adds rate limiting" or "Added rate limiting" — not "This PR will add rate limiting".
- No "This PR..." preambles. Start with the verb or the subject.
- Sacrifice grammar for concision. Full sentences are optional inside bullets.

## 30-second self-review before submit

Before posting or updating a PR body, scan it against this checklist:

- [ ] Can a reviewer who doesn't know the context pick this up cold?
- [ ] Any claim I can't back up? (especially "tested", "no regressions", "safe")
- [ ] Anything that would embarrass us if this repo went public tomorrow?
- [ ] Did I list both how to verify *and* what to look for?
- [ ] Did I explicitly call out what I did *not* test?
- [ ] Any breaking changes, deletions, or feature flags I forgot to flag?
