---
name: argos-pr-review
description: Review an Argos CI visual regression build for a pull request using the @argos-ci/cli. Use whenever an Argos check is failing, pending, or flagged as "needs review" on a PR, when the user mentions Argos, argos-ci, visual regression, snapshot diff, visual diff, visual snapshot, or pastes an app.argos-ci.com build URL. Also trigger when the user asks to review, verify, approve, inspect, or compare visual changes/snapshots/screenshots on a PR, or says things like "check argos", "review the argos build", "are the visual diffs intentional", or "why is argos red". Proactively invoke on any UI-affecting PR where an Argos check exists and is not green.
---

# Argos PR Review

Review an Argos build using the build itself, the pull request context, and any extra context the user provides. Produce a clear verdict on whether the visual diffs are intentional, expected, or regressions.

## Inputs you need

Before starting, collect:

- Argos build URL (e.g. `https://app.argos-ci.com/<org>/<repo>/builds/<N>`)
- PR URL or number
- PR title, description, and author — fetch via `gh pr view <PR>` if not given
- Any commit messages, linked issues, or user instructions that reveal intent

If the Argos build URL is not supplied, find it via `gh pr checks <PR>` or the PR's check list — the Argos check links to the build.

## CLI

Use the official Argos CLI.

- One-off (no global install): `npx @argos-ci/cli <command>`
- Global install (offer but do not run without confirmation): `npm install -g @argos-ci/cli`
- Help: `npx @argos-ci/cli --help`

## Authentication

1. Check CI files (`.github/workflows/*.yml`, `.env.example`, `argos.config.*`) for an `ARGOS_TOKEN` reference. If the token is exposed via the user's shell or a `.env` already loaded, use it.
2. Otherwise, ask the user to run `argos login` in their terminal — do not attempt interactive login inside the agent session.
3. Never paste tokens into logs, commit them, or write them to disk.

## Review procedure

1. **Check build status first.** If the build is `pending`, `failed`, `aborted`, or `incomplete`, stop and report that the build is not reviewable — include the exact status and the build URL.
2. **Enumerate snapshots needing review.** Only inspect snapshots Argos flags as changed/needing review. Ignore stable ones.
3. **Group duplicates.** If the same visual change appears across many snapshots (e.g. a shared header across 40 pages), inspect one representative. Inspect per-browser variants separately only when the diff differs across browsers.
4. **Compare base / head / diff for every distinct change.** Do not draw conclusions from the diff image alone — confirm by looking at base and head too.
5. **Infer intent.** Use the PR title, description, commits, code diff, linked issues, and user instructions. Map each visual change to a cause in the diff when possible (e.g. "Home route lazy-loads hero image → LCP panel shows shifted layout above the fold").
6. **Call out regressions or instability explicitly.** If a change looks unintentional, visually broken, cropped, or inconsistent (flakiness, anti-aliasing noise, font fallback), say so and cite the snapshot.
7. **Flag partial evidence.** If the build is missing browsers, skipped pages, or has stale baselines, say so — do not paper over gaps.
8. **Never approve or reject diffs on the user's behalf.** Approving Argos diffs is a Tier 4 action: recommend an action, let the user click.

## Required response format

Respond with exactly these four sections, in this order:

- **Inferred intent** — what the PR is trying to do, in one or two sentences.
- **Diffs reviewed** — list of distinct visual changes (grouped), with snapshot names/paths.
- **Evidence** — for each diff: base vs. head observation, and whether it matches intent.
- **Conclusion** — overall verdict: safe to approve, needs author attention, or blocked on missing evidence. Include a recommended next action.

If blocked, replace the sections with a single paragraph naming the exact blocker (e.g. "Build 14 is still running", "Missing ARGOS_TOKEN", "PR 222 has no Argos check").

## Scope guardrails

- Stay focused on the Argos build. Do not drift into unrelated code review, perf analysis, or refactor suggestions unless the user asks.
- Do not retry failed CLI calls in a loop. After 2–3 failures, report the blocker.
- Do not trigger browser alerts/dialogs or open interactive tools from the agent.
