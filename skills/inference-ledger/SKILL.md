---
name: inference-ledger
description: >
  Track every domain/product assumption the agent makes that isn't derivable from the
  repo, and force a user yes/no triage of the ledger BEFORE any PR opens or any external
  write (Asana, database, prod) happens. Use whenever work involves classifying,
  mapping, backfilling, or routing based on product knowledge — e.g. "which surfaces
  imply which browser", "which platforms a feature exists on", field mappings, taxonomy
  rules. Also invocable directly via /inference-ledger to review the current ledger.
---

# Inference Ledger

## The failure this prevents

Real incident: an agent derived "surface X implies Browser = DuckDuckGo" rules from
plausible product reasoning, got them reviewed by two bots, merged two PRs, and wrote
3,337 values to live Asana tasks. The user then corrected ~5 of the rules from product
knowledge no repo encodes (ATP blocks trackers in third-party apps; VPN is system-wide;
Duck.ai chats run in any browser). Undoing it took a 140-task clear-down and another PR.

Every one of those corrections was available in 30 seconds of user triage — *if the
inferences had been surfaced as a list before the writes.* That is this skill's job.

## What counts as an inference

An assertion used by the code/data change that is **not derivable from the repo's code,
data, schema, or docs**. Litmus test: "if the user disagreed with this sentence, would
the change be wrong?" If yes and no repo artifact settles it, it's an inference.

Typical shapes:
- "Product/feature X only exists on platform/browser Y"
- "Value A in field B implies value C in field D"
- "Users who answer X mean Y"
- "This category is being deprecated / is equivalent to that one"
- "This edge case is rare enough to ignore"

NOT inferences: facts read from code, live schema dumps, query results, official docs
you fetched, or things the user already stated this session (cite the statement instead).

## Procedure

1. **Tag at the moment of use.** When an inference enters the work, record it
   immediately in a running ledger (keep it in the session task list or a scratch file —
   never only in your head, never only in a code comment).

   Format per entry:
   ```
   N. [INFERENCE] <the claim, one sentence>
      basis: <why you believe it — product reasoning / help page / analogy>
      rides on it: <what breaks if wrong — e.g. "705 CPM tasks get Browser=DuckDuckGo">
   ```

2. **Attempt cheap verification first.** Before parking it as an inference, spend one
   step trying to settle it: repo docs, live schema, a ClickHouse query, an official
   help page (WebFetch). If settled, it's a fact with a citation — drop it from the
   ledger and cite the source in the code comment instead.

3. **Gate: present before external effects.** Before ANY of:
   - opening a PR,
   - writing to Asana / a database / prod,
   - handing the user something to paste into a live system,

   present the full ledger as a numbered list and ask for triage. Make the blast radius
   of each entry explicit. The user answers per-item: `yes` / `no` / `not sure`.
   - `no` → fix the change before proceeding.
   - `not sure` → treat as `no` for anything irreversible; proceed only on paths where
     the inference being wrong is cheap to undo, and say which paths those are.
   - **An untriaged ledger blocks external writes. It does not block local commits.**

4. **Zero-inference declaration.** If the ledger is empty at the gate, say so
   explicitly: "Inference ledger: empty — everything here traces to code, schema, or a
   cited source." Silence is not a declaration.

5. **Confirmed inferences become durable.** Any inference the user confirms or corrects
   is product truth the repo didn't have. Write it into the repo's domain doc (create
   `docs/DOMAIN-TRUTHS.md` if the repo has no better home), one line each with date and
   "confirmed by <user>". Next session's agent must find it there instead of re-deriving
   it. Corrections matter more than confirmations — record both.

## Presentation format at the gate

```
## Inference ledger — needs your triage before I <open PR / write to Asana / ...>

1. CPM implies Browser = DuckDuckGo
   basis: cookie pop-up management is a browser feature; no extension option in cpmPlatform
   rides on it: 705 tasks get Browser=DuckDuckGo
2. ...

Reply with e.g. "1 yes, 2 no, 3 not sure". Anything you correct gets written to
docs/DOMAIN-TRUTHS.md so no future session re-derives it.
```

Keep entries under 3 lines. Cap the list at what the user can triage in under 2 minutes;
if it's longer than ~10, the change is probably doing too much — say so.
