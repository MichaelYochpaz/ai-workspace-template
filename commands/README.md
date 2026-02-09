# Commands

Reusable AI commands/prompts invoked via `/command` syntax. Commands are defined here and automatically distributed to tool-specific directories.

## Creating a command

### 1. Create the command directory and command.md

Create a directory under `commands/` with a `command.md` file containing YAML frontmatter and prompt content:

```markdown
---
description: "Brief description for UI menus"
---

Your prompt instructions here.
Use natural language for tool invocation.
```

### 2. Validate and distribute

```bash
uv run .ai-workspace/scripts/transpile-commands.py
```

## Directory structure

```
commands/<command-name>/
└── command.md    # Frontmatter + prompt content
```

## Frontmatter

The only required field is `description`. Other fields are tool-specific and optional - each tool ignores fields it doesn't recognize, so you can combine fields for multiple tools in a single file.

```yaml
---
description: "Run tests and fix any failures"
allowed-tools: ["bash", "read_file", "edit_file"]
---
```

Refer to each tool's documentation for their supported frontmatter fields.

## Validation and distribution

```bash
# Validate only (also runs on pre-commit)
uv run .ai-workspace/scripts/transpile-commands.py --validate

# Validate + distribute to configured target directories
uv run .ai-workspace/scripts/transpile-commands.py
```

Distribution targets are configured in `ai-workspace.toml` under `distribution.commands_paths`. By default, all targets use **symlinks** - the target file points to the source `command.md`, so edits are reflected immediately.

### Distribution methods

| Method | Behavior |
|--------|----------|
| `symlink` | Default. Creates a symlink to the source file. |
| `strip_frontmatter` | Writes a copy with the YAML header removed. Use for tools that don't parse frontmatter. |

Some tools send frontmatter to the LLM as part of the prompt instead of parsing it as metadata. For example, at the time of writing, [Cursor](https://cursor.com/docs/context/commands) doesn't support frontmatter metadata in commands.

### Overriding the distribution method

Use `distribution.commands_overrides` in `ai-workspace.toml` to set `strip_frontmatter` for specific paths. Keys must match a path in `commands_paths`:

```toml
[distribution.commands_overrides]
".cursor/commands" = "strip_frontmatter"
".my-tool/commands" = "strip_frontmatter"
```

## Writing tips

- **Superset frontmatter** - Include metadata for all tools you use. Each tool ignores unknown keys.
- **Polyglot prompts** - Use natural language ("Use your terminal...") instead of tool-specific syntax so commands work across tools.
- **Single source of truth** - Write once here, distribute everywhere.
