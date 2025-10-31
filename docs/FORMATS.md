# Claude & Cursor Configuration Formats

## Directory Structures

### Claude Configuration (`.claude/`)

Claude uses the `.claude` directory in the user's home directory (`~/.claude/`) for global configuration:

```
~/.claude/
├── CLAUDE.md              # Global assistant rules
├── commands/               # Command definitions
│   ├── research.md
│   ├── plan.md
│   ├── implement.md
│   └── ...
├── agents/                 # Agent definitions
│   ├── file-finder.md
│   ├── code-analyzer.md
│   └── ...
├── settings.json           # IDE settings
└── sync-humanlayer-commands.py  # Utility scripts
```

**Key Files:**
- `CLAUDE.md` - Global rules that apply to all Claude interactions
- `commands/*.md` - Custom commands accessible via `/command-name`
- `agents/*.md` - Specialized agent definitions for parallel sub-tasks
- `settings.json` - IDE configuration (permissions, hooks, etc.)

### Cursor Configuration (`.cursor/`)

Cursor uses the `.cursor` directory in the user's home directory (`~/.cursor/`) for global configuration:

```
~/.cursor/
├── cli-config.json        # CLI configuration
├── ide_state.json         # IDE state
├── mcp.json              # MCP configuration
└── projects/             # Project-specific configs
```

**Project-Level Rules:**
Cursor also supports project-level rules files:
- `.cursorrules` in project root - Project-specific rules
- `.cursor/` directory in project root - Project-specific config

## File Formats

### Rules Files (`CLAUDE.md` / `.cursorrules`)

Both Claude and Cursor use Markdown format for rules:

**Format:**
```markdown
# Assistant Rules

## Section Name

- **Rule name** - Description of what to do
- **Another rule** - More details
```

**Key Characteristics:**
- Markdown format
- Section headers (##) for organization
- Bold action verbs (**Rule name**) for emphasis
- Bullet points for rules
- Short, actionable descriptions

### Command Files (`commands/*.md`)

**Format:**
```markdown
# Command Name

Description of what this command does.

## Instructions

Step-by-step instructions...
```

**Key Characteristics:**
- Markdown format
- Clear command name as H1
- Instructions section with numbered steps
- Can reference agents, tools, and other commands

### Agent Files (`agents/*.md`)

**Format:**
```markdown
# Agent Name

## Purpose

What this agent specializes in.

## Instructions

How to use this agent...
```

**Key Characteristics:**
- Markdown format
- Purpose-driven naming
- Specific instructions for agent behavior
- Focused on single responsibility

### Settings Files (`settings.json`)

**Format:**
```json
{
  "apiKeyHelper": "...",
  "env": {
    "disableTelemetry": "true"
  },
  "permissions": {
    "allow": ["Bash(git:*)"],
    "defaultMode": "plan"
  },
  "hooks": {
    "Notification": [...]
  }
}
```

## Compatibility Strategy

### agents-config Repository Approach

To maintain compatibility between Claude and Cursor:

1. **Primary Storage**: Store all configuration in `.agents-config/` repository
2. **Symlinks**: Create symlinks from IDE directories to `.agents-config/`
3. **IDE-Specific**: IDE directories contain only symlinks and IDE-specific files

### Symlink Structure

```
~/.claude/
├── CLAUDE.md -> ~/.agents-config/rules/CLAUDE.md
├── commands -> ~/.agents-config/commands/
└── agents -> ~/.agents-config/agents/

~/.cursor/
├── commands -> ~/.agents-config/commands/ (if supported)
├── agents -> ~/.agents-config/agents/ (if supported)
└── [cursor-specific files]
```

## Maintenance

Use `sync-to-ides.py` script to:
- Create/update symlinks from IDE directories to `.agents-config/`
- Verify symlink integrity
- Preserve IDE-specific files when syncing
- Report configuration status

## Differences & Notes

### Claude-Specific
- Uses `CLAUDE.md` for rules
- `commands/` directory for custom commands
- `agents/` directory for parallel sub-agents
- `settings.json` for IDE configuration

### Cursor-Specific
- Uses `.cursorrules` file in project root (not global)
- `cli-config.json` for CLI configuration
- `ide_state.json` for IDE state
- Project-specific `.cursor/` directories

### Shared Behavior
- Both use Markdown for rules/commands/agents
- Both support similar agent/command patterns
- Both can reference external files and tools
- Both support JSON for structured configuration

## Best Practices

1. **Keep rules in `.agents-config/rules/CLAUDE.md`** - Single source of truth
2. **Use symlinks** - Avoid duplication, maintain consistency
3. **Edit only in repo** - Never edit files directly in IDE directories
4. **Document additions** - Update this file when adding new formats
5. **Test both IDEs** - Verify changes work in both Claude and Cursor
6. **Version control** - Keep `.agents-config/` repo in git for portability


