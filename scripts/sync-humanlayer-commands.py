#!/usr/bin/env python3
"""
Sync HumanLayer commands from GitHub, filtering to research/plan/implement loop.
Removes HumanLayer-specific details while retaining agent guidance.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# Commands to sync (research/plan/implement loop)
COMMAND_MAPPING = {
    'research_codebase.md': 'research.md',
    'create_plan.md': 'plan.md',
    'implement_plan.md': 'implement.md',
    'validate_plan.md': 'validate-plan.md',
    'create_handoff.md': 'handoff.md',
    'resume_handoff.md': 'resume-handoff.md',
}

# Commands to exclude (CI, Linear, HumanLayer-specific)
EXCLUDED_COMMANDS = {
    'ci_commit.md', 'ci_describe_pr.md', 'commit.md', 'describe_pr.md',
    'linear.md', 'create_worktree.md', 'debug.md', 'founder_mode.md',
    'oneshot.md', 'oneshot_plan.md', 'ralph_impl.md', 'ralph_plan.md',
    'ralph_research.md', 'research_codebase_generic.md', 'research_codebase_nt.md',
    'create_plan_generic.md', 'create_plan_nt.md', 'local_review.md',
}

GITHUB_API_BASE = 'https://api.github.com/repos/humanlayer/humanlayer/contents/.claude/commands?ref=main'
GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/humanlayer/humanlayer/main/.claude/commands/'


def remove_yaml_frontmatter(content):
    """Remove YAML frontmatter if present"""
    if content.startswith('---\n'):
        end = content.find('\n---\n', 4)
        if end != -1:
            return content[end + 5:]
    return content


def transform_content(content, filename):
    """Transform content by removing HL-specific details"""
    # Remove YAML frontmatter
    content = remove_yaml_frontmatter(content)
    
    # Remove lines with specific HL references
    lines = content.split('\n')
    filtered_lines = []
    skip_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip blocks that reference HL-specific things
        if any(ref in line for ref in ['hack/spec_metadata.sh', 'scripts/spec_metadata.sh', 
                                       'humanlayer thoughts sync', 'thoughts/searchable/']):
            i += 1
            continue
        
        # Skip "Path handling" bullet block
        if '**Path handling**' in line or 'Path handling:' in line:
            skip_block = True
            i += 1
            continue
        
        # Skip "Frontmatter consistency" bullet block
        if '**Frontmatter consistency**' in line:
            skip_block = True
            i += 1
            continue
        
        # Stop skipping when we hit a new section or non-indented line
        if skip_block:
            if line.strip() and not line.startswith('  ') and not line.startswith('-') and not line.startswith('*'):
                skip_block = False
            else:
                i += 1
                continue
        
        filtered_lines.append(line)
        i += 1
    
    content = '\n'.join(filtered_lines)
    
    # Transform thoughts/ directory references to agent-docs/
    content = re.sub(r'thoughts/', 'agent-docs/', content)
    
    # Replace agent names (these are separate because they don't have trailing slash)
    content = re.sub(r'thoughts-locator', 'agent-docs-locator', content)
    content = re.sub(r'thoughts-analyzer', 'agent-docs-analyzer', content)
    
    # Special handling for research_codebase.md
    if filename == 'research_codebase.md':
        # Remove metadata gathering step
        content = re.sub(
            r'5\. \*\*Gather metadata for the research document:\*\*\s*\n.*?\n6\. \*\*Generate research document:\*\*',
            '5. **Generate research document:**',
            content,
            flags=re.DOTALL
        )
        
        # Replace research document template
        pattern = r'5\. \*\*Generate research document:\*\*\s*\n\s*- Use the metadata gathered in step 4\s*\n\s*- Structure the document with YAML frontmatter followed by content:\s*\n\s*```markdown\s*\n.*?```'
        replacement = '''5. **Generate research document:**
   - Create at `docs/ai/research/YYYY-MM-DD_topic-name.md`
   - Use this structure (no frontmatter):

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
```'''
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Remove sync step references
        content = re.sub(r'\s*- Run `humanlayer thoughts sync`.+\n', '\n', content)
        content = re.sub(r'\s*Run `humanlayer thoughts sync`.+\n', '\n', content)
        
        # Fix step 8
        content = re.sub(r'8\. \*\*Sync and present findings:\*\*\s*\n\s*- Run `humanlayer thoughts sync`.*?\n', '8. **Present findings:**\n', content, flags=re.DOTALL)
        if '8. **Present findings:**' not in content:
            content = re.sub(r'8\. \*\*Sync and present findings:\*\*\s*\n\s*- Present', '8. **Present findings:**\n   - Present', content, flags=re.DOTALL)
        
        # Fix step 9
        content = re.sub(
            r'9\. \*\*Handle follow-up questions:\*\*\s*\n\s*- If the user has follow-up questions.*?\n\s*- Update the frontmatter fields.*?\n\s*- Add `last_updated_note:.*?\n\s*- Add a new section:.*?\n\s*- Spawn new sub-agents.*?\n\s*- Continue updating the document and syncing',
            '9. **Handle follow-up questions:**\n   - If the user has follow-up questions, append to the same research document\n   - Add a new section: `## Follow-up Research [timestamp]`\n   - Spawn new sub-agents as needed for additional investigation\n   - Continue updating the document',
            content,
            flags=re.DOTALL
        )
        
        # Remove metadata and path handling references
        content = re.sub(r'\s*- ALWAYS gather metadata before writing.*?\n', '', content)
        content = re.sub(r'\s*- Always document paths by removing ONLY "searchable/".*?\n', '', content)
        content = re.sub(r'\s*- Examples of correct transformations:.*?\n', '', content)
        content = re.sub(r'\s*- NEVER change allison/ to shared/.*?\n', '', content)
        content = re.sub(r'\s*- This ensures paths are correct.*?\n', '', content)
        content = re.sub(r'\s*- Always include frontmatter.*?\n', '', content)
        content = re.sub(r'\s*- Keep frontmatter fields consistent.*?\n', '', content)
        content = re.sub(r'\s*- Update frontmatter when adding.*?\n', '', content)
        content = re.sub(r'\s*- Use snake_case for multi-word.*?\n', '', content)
        content = re.sub(r'\s*- Tags should be relevant.*?\n', '', content)
        
        # Fix step numbering
        content = re.sub(r'```\n\n7\. \*\*Add GitHub permalinks', '```\n\n6. **Add GitHub permalinks', content)
        content = re.sub(r'8\. \*\*Present findings:\*\*', '7. **Present findings:**', content)
        content = re.sub(r'9\. \*\*Handle follow-up questions:\*\*', '8. **Handle follow-up questions:**', content)
        
        # Fix formatting in notes section
        content = re.sub(
            r'- \*\*Critical ordering\*\*: Follow the numbered steps exactly\s*\n\s*- ALWAYS read mentioned files first before spawning sub-tasks \(step 1\)\s*\n\s*- ALWAYS wait for all sub-agents to complete before synthesizing \(step 4\)\s*\n\s*- NEVER write the research document with placeholder values\s*\n\s*- This ensures paths are correct for editing and navigation',
            '- **Critical ordering**: Follow the numbered steps exactly\n  - ALWAYS read mentioned files first before spawning sub-tasks (step 1)\n  - ALWAYS wait for all sub-agents to complete before synthesizing (step 4)\n  - NEVER write the research document with placeholder values',
            content,
            flags=re.DOTALL
        )
    
    # Handle create_handoff.md
    if filename == 'create_handoff.md':
        # Transform handoff paths (handle both original thoughts/ and transformed agent-docs/)
        content = re.sub(r'thoughts/shared/handoffs/ENG-XXXX/', 'docs/ai/handoffs/', content)
        content = re.sub(r'thoughts/shared/handoffs/', 'docs/ai/handoffs/', content)
        content = re.sub(r'agent-docs/shared/handoffs/ENG-XXXX/', 'docs/ai/handoffs/', content)
        content = re.sub(r'agent-docs/shared/handoffs/', 'docs/ai/handoffs/', content)
        content = re.sub(r'\s*- Run the `scripts/spec_metadata.sh`.+\n', '', content)
        content = re.sub(r'Structure the document with YAML frontmatter followed by content:', 'Use the following template structure:', content)
    
    return content.strip() + '\n'


def fetch_remote_files():
    """Fetch list of remote files from GitHub API"""
    try:
        req = Request(GITHUB_API_BASE)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        with urlopen(req) as response:
            files = json.loads(response.read())
            return [f['name'] for f in files if f['type'] == 'file' and f['name'].endswith('.md')]
    except URLError as e:
        print(f"Error fetching file list: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_file_content(filename):
    """Fetch file content from GitHub"""
    try:
        url = GITHUB_RAW_BASE + filename
        with urlopen(url) as response:
            return response.read().decode('utf-8')
    except URLError as e:
        print(f"Error fetching {filename}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description='Sync HumanLayer commands')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: dry-run)')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    parser.add_argument('--commands-dir', type=str, default='~/.claude/commands',
                       help='Commands directory (default: ~/.claude/commands)')
    args = parser.parse_args()
    
    commands_dir = Path(args.commands_dir).expanduser()
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch remote files
    print("Fetching file list from GitHub...")
    remote_files = fetch_remote_files()
    
    # Filter to only commands we want
    files_to_sync = {f: COMMAND_MAPPING[f] for f in COMMAND_MAPPING.keys() if f in remote_files}
    
    if not files_to_sync:
        print("No matching files found to sync.")
        return
    
    # Fetch and transform
    actions = []
    for remote_file, local_file in files_to_sync.items():
        print(f"Fetching {remote_file}...")
        content = fetch_file_content(remote_file)
        if content is None:
            continue
        
        transformed = transform_content(content, remote_file)
        
        # Compare with local
        local_path = commands_dir / local_file
        local_content = local_path.read_text() if local_path.exists() else None
        
        if local_content is None:
            action = 'CREATE'
        elif local_content.strip() == transformed.strip():
            action = 'UNCHANGED'
        else:
            action = 'UPDATE'
        
        actions.append({
            'remote': remote_file,
            'local': local_file,
            'action': action,
            'content': transformed
        })
    
    # Print summary
    print("\n" + "=" * 60)
    print("DRY-RUN SUMMARY")
    print("=" * 60)
    print("\nResearch/Plan/Implement Loop Commands:")
    print("-" * 60)
    for item in actions:
        if item['local'] in ['research.md', 'plan.md', 'implement.md', 'validate-plan.md']:
            print(f"{item['action']:12} {item['local']}")
            if item['remote'] != item['local']:
                print(f"             (from {item['remote']})")
    
    print("\nRelated Workflow Commands:")
    print("-" * 60)
    for item in actions:
        if item['local'] in ['handoff.md', 'resume-handoff.md']:
            print(f"{item['action']:12} {item['local']}")
            if item['remote'] != item['local']:
                print(f"             (from {item['remote']})")
    
    print("\n" + "=" * 60)
    print(f"Total: {len(actions)} files")
    print(f"  CREATE: {sum(1 for a in actions if a['action'] == 'CREATE')}")
    print(f"  UPDATE: {sum(1 for a in actions if a['action'] == 'UPDATE')}")
    print(f"  UNCHANGED: {sum(1 for a in actions if a['action'] == 'UNCHANGED')}")
    print("=" * 60)
    
    # Apply changes if requested
    if args.apply:
        if not args.yes:
            response = input("\nApply these changes? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Aborted.")
                return
        
        print("\nApplying changes...")
        for item in actions:
            if item['action'] != 'UNCHANGED':
                local_path = commands_dir / item['local']
                local_path.write_text(item['content'])
                print(f"  ✓ {item['action']:8} {item['local']}")
        
        print("\nDone! Files synced from humanlayer/humanlayer@main")
    else:
        print("\nThis is a dry-run. Use --apply to write changes, or --apply --yes to skip confirmation.")


if __name__ == '__main__':
    main()

