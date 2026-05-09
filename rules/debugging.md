# Debugging

## Don't dismiss user-reported bugs

If the user says something is broken, investigate deeper.

- Playwright passing does not prove production is correct. Automated tests cover the paths you wrote — they miss the ones you didn't.
- Never say "works for me" based on automated tests alone. If you can't reproduce, ask for repro steps before declaring no-bug.
- Reproduce in the same environment the user used (browser, viewport, auth state) — staging != prod, dev != Cloudflare Workers, etc.
- If the bug report is vague, ask for one missing detail at a time, not a questionnaire.

## Confirm understanding before acting

- Before proposing a solution, restate what you think the problem is in one sentence. Wait for confirmation only if there's genuine ambiguity.
- Don't suggest alternative approaches the user didn't ask for. When the user picks a direction, follow it without debating.
- "I'd actually do it differently" is fine to say once. Twice is nagging.

## Bounded loops only

Scripts and automated loops MUST have:

- A completion/exit condition.
- A maximum iteration cap (e.g. `MAX_ITER=20`).
- A way to surface progress (so the user can see where it stopped).

Never run unbounded loops. If you find yourself writing `while true`, stop and add a guard.

## UI feedback: look for adjacent issues

When the user reports a UI bug or UX problem, before fixing just the reported issue, spend 60 seconds scanning the same component or flow for adjacent problems of the same class.

- Bug report: "modal too tall" → check: no dismiss button? bad contrast? mobile broken?
- Bug report: "button not visible enough" → check: accessible on mobile? keyboard? right aria-label?
- Bug report: "form errors are confusing" → check: empty state? loading state? success state?

Report adjacent issues and fix them in the same change. Don't make the user report each one separately.

## Root cause vs quick fix

- Default to root cause. If the symptom is "the test flakes", find why; don't add a retry.
- Quick-fix is acceptable when:
  - The user explicitly asks for a tactical patch.
  - The root cause requires a Tier 4 decision (e.g. infra change) and the symptom is blocking.
  - The cost of full investigation outweighs the cost of the bug.
- When choosing a quick-fix over root cause, log it as Tier 2 in the commit/PR: "Quick fix; root cause is X, follow-up tracked in #Y."
