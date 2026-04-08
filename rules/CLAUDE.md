# Assistant Rules

## Code Quality & Testing

- **Lint and test before every commit** - Do not commit without running lint and test
- **Fix failing tests** - Never skip failing tests. Investigate root cause or ask user for clarification
- **Follow engineering best practices** - Prioritize readability, maintainability, robustness, and correctness in all code
- **Minimize code** - Write only what's needed. Reuse existing code when possible
- **Cleanup before commit** - After implementation works, use `/cleanup` command to simplify and remove excess complexity before committing

## Communication & Documentation

- **Be concise** - Sacrifice grammar for concision in all interactions and commit messages
- **Review latest docs** - Check for and review latest documentation before starting work
- **Use PR templates** - Always use .github PR templates when they exist
- **Succinct commits** - Keep commit messages short and factual
- **Succinct PRs** - PR descriptions should describe what changed and why/how. Avoid marketing language

## Planning & Execution

- **Create todo plan first** - Always make a plan with todos and get approval before starting work
- **Ask when unclear** - Never make assumptions. Always ask clarifying questions when anything is unclear
- **Parallelize with subagents** - When a task has 2+ independent parts (e.g. changes to different repos, unrelated file edits, research + implementation), use subagents to do them in parallel. The main context should coordinate, not do all the work sequentially

## Debugging

- **Don't dismiss user-reported bugs** - If the user says something is broken, investigate deeper. Playwright passing doesn't mean production behavior is correct. Never say "works for me" based on automated tests alone
- **Confirm understanding before acting** - Before proposing a solution, confirm you understand the actual request. Don't suggest alternative approaches the user didn't ask for. When the user picks a direction, follow it without debating
- **Bounded loops only** - Scripts and automated loops MUST have a completion/exit condition and a maximum iteration cap. Never run unbounded loops

## CI/CD

- **Check before changing** - Before making CI/build changes, verify: 1) lock files present and committed, 2) env var names match between local and deploy platform, 3) dependency compatibility. Commit lock files with every dependency change
- **Lock files are required** - Cloudflare Workers builds and most CI need the lock file (bun.lock, pnpm-lock.yaml, package-lock.json) committed. Never .gitignore them

## Repository Maintenance

- **Sync commands from upstream** - Use the `sync-commands` skill to pull latest from humanlayer and audit changes
- **Local conventions** - This repo uses `agent-docs/` (not `thoughts/`) and dashes in command names (not underscores)
