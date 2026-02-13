---
title: Workspace Development Guide
description: |
  How to modify, configure, and extend this workspace.
  Covers configuration, AGENTS.md generation, package management,
  creating agent-docs/skills/commands, tool discovery, and session hooks.
when: |
  When modifying workspace infrastructure or configuration. When creating
  or editing agent-docs, skills, or commands. When updating AGENTS.md,
  README.md, or AGENTS.project.md. When adding dependencies or changing
  ai-workspace.toml. When adding session hook support for a new AI tool.
---

# Workspace Development Guide

## Documentation Philosophy

- **AGENTS.md** - Instruction-oriented for AI agents. Operational guidelines, commands, and workflows.
- **README.md** - Explanation-oriented for human developers. Context, motivation, and conceptual understanding.

Consider the audience when updating each file.

## Design Principles

Follow these when contributing to the workspace:

- **Model agnostic** - Use only features available to any AI model or tool
- **Context-rich** - Provide enough information for autonomous work; unrelated topics belong in separate modules
- **Fully automated** - Workflows run start to finish with no manual steps or user input
- **Efficient** - Focus on specific topics, be concise, cut redundancy. Bloated docs waste tokens and confuse models
- **Respect conventions** - Follow submodule-specific instructions; workspace-level AGENTS.md takes priority on conflicts

## Configuration

The workspace is configured via `ai-workspace.toml` at the repository root.

Configuration is applied at two points:
1. **Alignment script** (`align-workspace.py`) - Manages feature directories, regenerates AGENTS.md, validates skills/commands
2. **Session start** (`session-start.py`) - Reports repository status, discovers CLI tools

After changing config, agent docs, or `AGENTS.project.md`, regenerate workspace files:

```bash
uv run .ai-workspace/scripts/align-workspace.py
```

Pre-commit hooks verify alignment on every commit (see [Pre-commit](#pre-commit) below) but do not apply changes. Run the script above before committing.

For the full configuration reference, see `.ai-workspace/docs/configuration.md`.

## AGENTS.md Generation

`AGENTS.md` is auto-generated - edit the source files, not the generated output.

| What to change | Edit |
|---|---|
| Project-specific agent instructions | `AGENTS.project.md` (repo root) |
| Workspace-level structure/instructions | `.ai-workspace/templates/AGENTS.md.j2` |

`AGENTS.project.md` content is injected under a "Project-Specific Context" heading. Remove the `<placeholder>` tags when adding content.

Regenerate manually:

```bash
uv run .ai-workspace/scripts/align-workspace.py
```

### Template Variables

The Jinja2 template receives these variables:

- `features.agent_docs.enabled` (bool), `features.agent_docs.docs` (list of `display_name`, `description`, `when_to_read`, `doc_path`)
- `features.skills.enabled` (bool), `features.skills.count` (int)
- `features.commands.enabled` (bool), `features.commands.count` (int)
- `project_content` (str or None)

For details, see `.ai-workspace/docs/agents-md.md`.

## Package Management

Use `uv` for all package operations:

```bash
uv add <package>                   # Add dependency (tracked in pyproject.toml)
uv add --dev <package>             # Add dev dependency
uv sync                            # Install/update all dependencies
uv run <script>                    # Run with project dependencies
```

For scripts with inline dependencies (PEP 723), run them directly with `uv run script.py` - this lets uv resolve inline deps automatically.

## Agent Resources

### Agent Docs

Modular, task-focused documentation that agents selectively load based on relevance. Each doc lives in `agent-docs/` as a markdown file with YAML frontmatter containing a `title`, `description`, and `when` field. At session start, agents see the list of titles and descriptions (injected into AGENTS.md), then read the full content of relevant docs before starting a task.

The `when` field is critical - it drives relevance matching. Write it to describe specific situations where the doc should be consulted (e.g., "When adding a new API endpoint" rather than just "When working on APIs").

See `agent-docs/README.md` for how to create and structure agent docs.

### Skills

Reusable agent capabilities following the [Agent Skills specification](https://agentskills.io/specification). Each skill is a directory under `skills/` containing a `SKILL.md` (frontmatter + instructions) and optional scripts, references, and assets. Agents load `name` + `description` at startup (~100 tokens) and only load the full `SKILL.md` when the skill is activated.

Skills are distributed to tool-specific directories via symlinks, configured in `ai-workspace.toml` under `distribution.skills_paths`. The transpile script validates frontmatter and creates the symlinks.

After creating or modifying skills, validate and distribute them, by running:

```bash
uv run .ai-workspace/scripts/transpile-skills.py
```

This validates skill structure and creates symlinks to tool-specific directories. Use `--validate` only when checking structure without distributing (e.g., during iterative development).

See `skills/README.md` for how to create and validate skills.

### Commands

Reusable AI prompts invoked via `/command` syntax. Each command lives in `commands/<name>/command.md` with YAML frontmatter (at minimum a `description` field) followed by the prompt content. Commands are written once and distributed to multiple tool-specific directories, so the same command works across different AI tools.

Distribution targets and methods are configured in `ai-workspace.toml` under `distribution.commands_paths` and `distribution.commands_overrides`. By default, commands are symlinked; tools that don't parse frontmatter metadata need the `strip_frontmatter` distribution method configured via overrides.

After creating or modifying commands, validate and distribute them, by running:

```bash
uv run .ai-workspace/scripts/transpile-commands.py
```

This validates command structure and distributes to tool-specific directories. Use `--validate` only when checking structure without distributing (e.g., during iterative development).

See `commands/README.md` for how to create commands and configure distribution.

## Tool Discovery

Define CLI tools in `agent-tools.yaml` (repo root). At session start, the script checks each tool's command on PATH and injects available tools into agent context.

```yaml
<tool-id>:
  command: <executable>        # Required - checked on PATH
  name: <display-name>        # Optional
  description: <brief-desc>   # Optional
  when_to_use: |              # Optional
    - Condition 1
  instructions: |             # Optional
    Common commands:
    - example 1
```

For details, see `.ai-workspace/docs/features/tool-discovery.md`.

## Session Hooks

Session hooks inject context (repository status, available tools) into AI agents at session start. Hook configs are committed to the repo and work out of the box for supported tools.

To add support for a new AI tool:

1. Add a formatter to `.ai-workspace/scripts/session-start.py` in the `FORMATTERS` dict, matching the tool's expected JSON schema
2. Create the tool's hook config file pointing to: `uv run .ai-workspace/scripts/session-start.py --tool <name>`

If the tool captures stdout as plain text (no JSON protocol), skip step 1 and call the script with no arguments.

For supported tools and details, see `.ai-workspace/docs/development/session-hooks.md`.

## Initial Setup

```bash
uv sync
uv run .ai-workspace/scripts/setup.py
```

This installs dependencies, initializes submodules, installs pre-commit hooks, and generates AGENTS.md. Safe to re-run.

### Adding Submodules

```bash
git submodule add <repository-url> repositories/<path>
```

For submodule management, branch tracking, and commit workflow, see `.ai-workspace/docs/repositories.md`.
