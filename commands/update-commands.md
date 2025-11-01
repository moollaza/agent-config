# Update Commands from HumanLayer

Sync the latest `.claude/commands` from `humanlayer/humanlayer@main` into this workspace, filtering to only research/plan/implement loop commands and removing HumanLayer-specific details while retaining useful agent guidance.

## Quick Start

**Recommended:** Use the automated script:
```bash
python3 ~/.claude/sync-humanlayer-commands.py          # Dry-run
python3 ~/.claude/sync-humanlayer-commands.py --apply   # Apply changes
python3 ~/.claude/sync-humanlayer-commands.py --apply --yes  # Skip confirmation
```

If you prefer manual control or the script isn't available, follow the steps below.

## When invoked

Say: "I'm ready to sync HumanLayer commands. I'll fetch from main and show a dry-run of changes. Reply with 'apply --yes' to write changes, or 'cancel' to abort."

Then proceed with a dry-run unless the user immediately replies with `apply --yes`.

## Goals

- **Filter to research/plan/implement loop commands only** (exclude CI, Linear, HumanLayer-specific commands)
- Keep commands aligned with the latest HumanLayer commands.
- Remove HumanLayer-specific scripts and directory semantics.
- Keep references to HumanLayer agents and emphasize parallel sub-agents.
- Overwrite local files only after confirmation.

## Commands to Sync

Only sync these research/plan/implement loop commands:
- `research_codebase.md` → `research.md`
- `create_plan.md` → `plan.md`
- `implement_plan.md` → `implement.md`
- `validate_plan.md` → `validate-plan.md`
- `create_handoff.md` → `handoff.md`
- `resume_handoff.md` → `resume-handoff.md`

## Commands to Exclude

Do NOT sync these (CI, Linear, HumanLayer-specific, or variants):
- CI commands: `ci_commit.md`, `ci_describe_pr.md`, `commit.md`, `describe_pr.md`
- Linear-specific: `linear.md`
- HumanLayer-specific: `ralph_*`, `create_worktree.md`, `founder_mode.md`, `oneshot*`, `debug.md`
- Variants: `*_generic.md`, `*_nt.md`, `local_review.md`

## Inputs (natural language is fine)

- apply: apply changes (default: false)
- yes: skip confirmation when applying (default: false)
- include/exclude: optional filename filters

## Steps

1. Discover remote files

   - Source: `https://api.github.com/repos/humanlayer/humanlayer/contents/.claude/commands?ref=main`
   - Build a list of `.md` files to consider (apply include/exclude filters if provided).

2. Fetch contents (from main)

   - Raw base: `https://raw.githubusercontent.com/humanlayer/humanlayer/main/.claude/commands/{name}`
   - Retrieve raw text for each file.

3. Transform content (remove HL-specific, keep agents)

   - Remove YAML frontmatter if present (a leading `---` block ending with `\n---\n`).
   - Transform directory references:
     - Replace `thoughts/` → `agent-docs/` (all directory paths)
     - Replace `thoughts-locator` → `agent-docs-locator`
     - Replace `thoughts-analyzer` → `agent-docs-analyzer`
   - Remove lines or sections that are HumanLayer-specific:
     - Any reference to `hack/spec_metadata.sh`
     - Any reference to `humanlayer thoughts sync`
     - Any reference to `thoughts/searchable/` and its path handling rules
     - Remove the "Path handling" bullet block and the "Frontmatter consistency" bullet block if present
   - Keep references to HumanLayer agents and parallel sub-agents guidance (do NOT remove these):
     - codebase-locator, codebase-analyzer, codebase-pattern-finder
     - agent-docs-locator, agent-docs-analyzer (optional to use if a local notes dir exists)
     - web-search-researcher (only if explicitly needed)
     - linear-ticket-reader, linear-searcher (if relevant)

4. Special-case file mappings and transformations
   
   **`research_codebase.md` → `research.md`:**
   - Ensure strong "documentarian only" rules (document what exists; no critique, no improvements).
   - Replace the "Generate research document" section and template with this no-frontmatter structure at `docs/ai/research/YYYY-MM-DD_topic-name.md`:

```markdown
# Research: [Topic]

## Research Question

[Original user query]

## Summary

[2-3 paragraph high-level summary of findings]

## Detailed Findings

### Component: [Name]

- **Purpose**: What this component does
- **Location**: `path/to/file.ext:123`
- **How It Works**: [Explanation]
- **Key Functions**:
  - `functionName` (line 45): [Description]
- **Dependencies**: What it depends on
- **Used By**: What depends on it

### Component: [Name]

[Repeat for each major component...]

## Code Flow

1. Entry point: `file.ext:123`
2. Flows to: `other.ext:456`
3. Returns to: `caller.ext:789`

## Patterns & Conventions

- **Pattern Name**: How and where it's used
- **Convention**: Observed convention with examples

## Architecture Notes

[Important architectural decisions or design patterns]

## Key Files Reference

- `path/to/important.file` - [Role in system]
- `path/to/config.file` - [What it configures]

## Open Questions

[Anything unclear or needing investigation]
```

   **`create_handoff.md` → `handoff.md`:**
   - Replace `agent-docs/shared/handoffs/ENG-XXXX/` paths with `docs/ai/handoffs/`
   - Remove references to `scripts/spec_metadata.sh`
   - Simplify frontmatter requirements (remove YAML requirement)
   
   **All other files:** Apply HL-specific removals but keep the same filename locally.

5. Compute actions and show dry-run

   - For each destination file, compare transformed content with the current local content.
   - Mark as `CREATE`, `UPDATE`, or `UNCHANGED`.
   - Present a concise summary of planned changes.

6. Apply changes (only if requested)

   - If the user responds with `apply --yes`, write the files.
   - Otherwise, keep it as a dry-run and exit without changes.

7. Report results
   - List written files with their actions.
   - Note that the source was `humanlayer/humanlayer@main`.

## Notes

- **Default behavior is safe: dry-run only.**
- Overwrites are allowed only after explicit confirmation.
- **Prefer using the automated script** (`~/.claude/sync-humanlayer-commands.py`) for faster, more reliable syncing.
- The script automatically filters to only research/plan/implement commands.
- If running manually, ensure you filter to only the commands listed in "Commands to Sync" above.
- The agent should prefer parallel fetches and transformations to be fast.

## Implementation Notes

- The base `research_codebase.md` version is preferred over `research_codebase_generic.md` because it includes the critical "documentarian only" emphasis and detailed agent guidance.
- The base `create_plan.md` version is preferred over `create_plan_generic.md` because it includes `make` command guidance and directory specificity.

## References

- HumanLayer commands repository: https://github.com/humanlayer/humanlayer/tree/main/.claude/commands
- Sync script: `~/.claude/sync-humanlayer-commands.py`
