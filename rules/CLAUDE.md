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

## Repository Maintenance

- **Sync commands from upstream** - Use the `sync-commands` skill to pull latest from humanlayer and audit changes
- **Local conventions** - This repo uses `agent-docs/` (not `thoughts/`) and dashes in command names (not underscores)
