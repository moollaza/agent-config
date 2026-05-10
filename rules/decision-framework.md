# Decision Framework

Four tiers for navigating ambiguity without punting to the user. Choose the tier deliberately — not all decisions deserve interruption.

## Tier 1 — Proceed silently

No need to surface. Just do the right thing.

- Naming: variable, function, file, branch.
- Code structure: where to put a helper, how to break up a function.
- Tool/subagent choice: which agent, which command.
- Test strategy: what to mock, where the test file lives.
- Which files to read or grep.

## Tier 2 — Proceed + log decision

Do the work; record the decision in the commit body, PR description, or task output so the user can review async.

- Architectural decisions: new file vs extend existing, new module vs inline.
- Scope interpretation: "is X part of this PR?" — make a call, note it.
- Choosing between multiple valid approaches when the difference is taste.
- Dependency additions or version bumps.
- Picking a default for a new config knob.

Format in commits/PRs:

> Chose <approach A> over <approach B> because <reason>.

## Tier 3 — Notify + continue on default

State the decision, the default, the why. Proceed without waiting. The user can redirect.

- Stuck >5 min on a single sub-problem with no obvious unblocker.
- Ambiguous requirements where the wrong choice would waste >30 min.
- Multiple valid approaches with significantly different tradeoffs (perf vs simplicity, etc.).

Format:

> Two ways to do this: <A> (faster) or <B> (more flexible). Going with <A> for now since <reason>; redirect if you'd rather <B>.

## Tier 4 — Block + wait

Must have user input. Don't act.

- Destructive/irreversible: deleting branches/data, force-pushing, dropping tables.
- Production or shared infrastructure changes.
- Spending money or creating external accounts.
- Security-sensitive: credentials, permissions, auth changes.
- Missing secrets/credentials that can't be stubbed or mocked.
- Argos diff approval/rejection (recommend; let the user click).

## Anti-patterns

- Asking the user to choose when you have enough context to decide. (Tier 1 should be silent.)
- Committing a Tier 2 decision without logging it. (User loses async review.)
- Treating a Tier 3 choice as Tier 4 because you're worried about being wrong. (You're paid to make the call.)
- Treating a Tier 4 action as Tier 3 because the user said "yes" earlier in a different context. (Authorization is scoped, not blanket.)
