# Commands

Different AI tools expect commands in different directories and formats. This workspace lets you maintain commands in one place (`commands/`) and automatically distributes them to the right locations, converting formats where needed.

## What this workspace does

1. **Single source of truth** - You write commands in `commands/<name>/command.md`
2. **Validation** - The transpile script checks that frontmatter is valid YAML with a `description` field
3. **Distribution** - Commands are distributed to configured target directories
4. **Pre-commit integration** - Validation runs automatically on every commit

## Directory structure

```
commands/
└── <command-name>/
    └── command.md    # Frontmatter + prompt content
```

## Frontmatter

Commands use YAML frontmatter to define metadata. Each tool supports its own fields, but tools ignore fields they don't recognize - so you can combine fields for multiple tools in a single file.

```yaml
---
description: "Run tests and fix any failures"
allowed-tools: ["bash", "read_file", "edit_file"]
---

Your prompt instructions go here.
```

The only **required** field is `description`. Everything else is tool-specific and optional. Refer to each tool's documentation for their supported fields.

## Distribution

```bash
# Validate + distribute
uv run .ai-workspace/scripts/transpile-commands.py

# Validate only (used by pre-commit)
uv run .ai-workspace/scripts/transpile-commands.py --validate
```

### How distribution works

Commands are distributed to every path listed in `commands_paths` in `ai-workspace.toml`. By default, all targets use **symlinks** - the target file is a symlink pointing to the source `command.md`. This means edits to the source are immediately reflected everywhere.

Some tools don't support frontmatter metadata and will send the YAML header to the LLM as part of the prompt. For these tools, use the **strip_frontmatter** distribution method - it writes a copy of the command with the YAML header removed.

For example, at the time of writing, [Cursor](https://cursor.com/docs/context/commands) doesn't support frontmatter metadata in commands. To handle this, add an override in `ai-workspace.toml`:

```toml
[distribution]
commands_paths = [
    ".claude/commands",
    ".cursor/commands",
]

[distribution.commands_overrides]
".cursor/commands" = "strip_frontmatter"
```

### Distribution methods

| Method | Behavior |
|--------|----------|
| `symlink` | Default. Creates a symlink to the source file. |
| `strip_frontmatter` | Writes a copy with the YAML frontmatter removed. |

### Configuring distribution targets

Add or remove paths in `commands_paths`. Use `commands_overrides` to change the method for specific paths:

```toml
[distribution]
commands_paths = [
    ".claude/commands",
    ".cursor/commands",
    ".my-tool/commands",
]

[distribution.commands_overrides]
".cursor/commands" = "strip_frontmatter"
".my-tool/commands" = "strip_frontmatter"
```

Override keys must match a path in `commands_paths`. Unmatched overrides are ignored with a warning - this lets you pre-configure overrides for paths you may add later.

See [Configuration](../configuration.md#distribution) for the full reference.
