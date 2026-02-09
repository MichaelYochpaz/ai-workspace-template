# Configuration

The workspace is configured via `ai-workspace.toml` at the repository root. Most settings have sensible defaults - distribution paths must be explicitly configured for your project.

## Full example

Here's a complete config file showing all settings.  
Distribution paths (`skills_paths`, `commands_paths`) default to empty and must be configured for your tools:

```toml
[repositories]
include_workspace_root = false

[features]
skills = true
commands = true
agent_docs = true

[tools]
show_unavailable = false

[distribution]
skills_paths = [".opencode/skill"]
commands_paths = [
    ".claude/commands",
    ".cursor/commands",
    ".opencode/command",
]

[distribution.commands_overrides]
".cursor/commands" = "strip_frontmatter"
```

---

## Repositories

Controls repository status reporting at session start. Section: `[repositories]`

`include_workspace_root`
:   **Type:** bool - **Default:** `false`

    Include the workspace root repo in session status

The default branch for each submodule is auto-detected at session start. If detection fails (e.g., a submodule uses a non-standard default branch like `develop`), set the `branch` field in `.gitmodules` for that submodule.  
See [Repositories](repositories.md#default-branch-detection) for details.

---

## Session hooks

Session hooks are pre-configured in each tool's config directory - they're committed to the repo and work out of the box. No configuration needed.

The session-start script runs repository status reporting and tool discovery, then injects the results into the agent's context. See [Session Hooks](development/session-hooks.md) for supported tools and details.

---

## Features

Enable or disable workspace features. Section: `[features]`

`skills`
:   **Type:** bool - **Default:** `true`

    Enable the skills system (`skills/` directory)

`commands`
:   **Type:** bool - **Default:** `true`

    Enable the commands system (`commands/` directory)

`agent_docs`
:   **Type:** bool - **Default:** `true`

    Enable the agent-docs system (`agent-docs/` directory)

**What happens when you change these:**

- **Enabling** a feature creates its directory with a README if it doesn't exist
- **Disabling** a feature removes its directory **only if it's empty** (or contains just a README).  
If the directory has user content, pre-commit fails with instructions to manually remove the files first

!!! note

    This prevents accidental data loss while letting you cleanly disable unused features.

---

## Tools

Controls the [Tool Discovery](features/tool-discovery.md) feature. Section: `[tools]`

`show_unavailable`
:   **Type:** bool - **Default:** `false`

    Show all defined tools with availability status, or only available ones

**Behavior:**

- `false` (default) - Only tools found on the system PATH are shown to agents. Clean and focused.
- `true` - All tools are shown with `available="true"` or `available="false"`. Useful when you want agents to know about tools they *could* use if installed.

Tools themselves are defined in `agent-tools.yaml` at the repo root, not in this config file. See [Tool Discovery](features/tool-discovery.md) for details on defining tools.

---

## Distribution

Controls where skills and commands are distributed for different AI tools. Section: `[distribution]`

Distribution paths default to empty - you must explicitly configure them for the tools you use.

`skills_paths`
:   **Type:** list[str] - **Default:** `[]`

    Target directories for skills symlinks

`commands_paths`
:   **Type:** list[str] - **Default:** `[]`

    Target directories for commands

`commands_overrides`
:   **Type:** dict[str, str] - **Default:** `{}`

    Override distribution method for specific command paths. Keys are paths from `commands_paths`, values are distribution methods (`symlink` or `strip_frontmatter`). Overrides for paths not yet in `commands_paths` are kept for future use (a warning is printed during distribution).

### Distribution methods

Skills and commands in their source directories (`skills/`, `commands/`) are the source of truth. The transpile scripts distribute them to tool-specific directories:

| Method | How it works |
|--------|-------------|
| **Symlink** | Default for all paths. Creates a symlink pointing to the source file/directory. |
| **Strip frontmatter** | Writes a copy with the YAML frontmatter removed. Use for tools that don't parse frontmatter. |

The `strip_frontmatter` method is needed for tools that send frontmatter to the LLM as part of the prompt instead of parsing it as metadata. For example, at the time of writing, [Cursor](https://cursor.com/docs/context/commands) doesn't support frontmatter metadata in commands.

### Configuring distribution

Add your tool's paths to the appropriate list. Use `commands_overrides` to set `strip_frontmatter` for tools that need it:

```toml
[distribution]
skills_paths = [
    ".opencode/skill",
]
commands_paths = [
    ".claude/commands",
    ".cursor/commands",
    ".opencode/command",
]

[distribution.commands_overrides]
".cursor/commands" = "strip_frontmatter"
```

See [Commands](features/commands.md#distribution) for more details on how distribution works.

---

## How configuration is applied

Configuration is applied at two points:

1. **Pre-commit** (`align-workspace.py`) - Reads `ai-workspace.toml` and:
    - Manages feature directories (create/remove based on `[features]`)
    - Renders `AGENTS.md` from the Jinja2 template
    - Runs skill and command validators

2. **Session start** (`session-start.py`) - Reads `ai-workspace.toml` and:
    - Reports repository status based on `[repositories]` settings
    - Discovers tools based on `[tools]` settings

After changing `ai-workspace.toml`, run pre-commit to apply:

```bash
uv run pre-commit run --all-files
```

## AGENTS.md generation

`AGENTS.md` is auto-generated from a Jinja2 template and your project-specific content. See [AGENTS.md Generation](agents-md.md) for how the template system works, available template variables, and customization options.
