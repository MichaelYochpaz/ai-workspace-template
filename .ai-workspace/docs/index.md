# AI Workspace Template

A meta-repository template that aggregates related repositories using git submodules, creating a unified workspace for AI agents to operate across your project ecosystem.

## Features

<div class="grid cards" markdown>

-   :material-source-repository:{ .lg .middle } __Repositories__

    ---

    Aggregate repos as submodules with automatic git status reporting to agents

    [Learn more :material-arrow-right:](repositories.md)

-   :material-file-document-outline:{ .lg .middle } __Agent Docs__

    ---

    Modular docs that agents selectively load based on task relevance

    [Learn more :material-arrow-right:](features/agent-docs.md)

-   :material-file-cog:{ .lg .middle } __AGENTS.md Generation__

    ---

    Auto-generate agent instructions from templates and config on every commit

    [Learn more :material-arrow-right:](agents-md.md)

-   :material-magnify:{ .lg .middle } __Tool Discovery__

    ---

    Detect installed CLI tools and inject usage instructions into agent context

    [Learn more :material-arrow-right:](features/tool-discovery.md)

-   :material-lightning-bolt:{ .lg .middle } __Skills__

    ---

    Distribute skill directories to tool-specific paths via symlinks

    [Learn more :material-arrow-right:](features/skills.md)

-   :material-console:{ .lg .middle } __Commands__

    ---

    Distribute command files across tools, converting formats where needed

    [Learn more :material-arrow-right:](features/commands.md)

-   :material-folder-clock:{ .lg .middle } __Temporary Files__

    ---

    Git-ignored workspace for agent artifacts, organized by task

    [Learn more :material-arrow-right:](features/temporary-files.md)

</div>

## How it works

### Session hooks

Some AI tools support **hooks** - scripts that run automatically at specific lifecycle points (e.g., session start, pre-prompt). This workspace uses a session-start hook to inject context into the agent before it begins work.

For tools with hook support ([Claude Code](https://code.claude.com/docs/en/hooks), [OpenCode](https://opencode.ai/docs/plugins/), [Cursor](https://cursor.com/docs/agent/hooks), [Gemini CLI](https://geminicli.com/docs/hooks/)), the session-start script runs automatically when an AI session begins:

``` mermaid
graph LR
  A[AI Session Starts] --> B[Session Hook Fires]
  B --> C[Fetch Repo Status]
  B --> D[Discover CLI Tools]
  C --> E[Inject Context into Agent]
  D --> E
```

The agent immediately knows which repos exist, what branch each is on, whether there are uncommitted changes, and which CLI tools are available.

### Pre-commit validation

Separately, on every commit, pre-commit hooks keep the workspace aligned:

- Regenerate `AGENTS.md` from templates and config
- Validate skill and command definitions
- Sync workspace structure with config

These are two independent flows - session hooks handle runtime context, pre-commit handles workspace integrity.

!!! info "Other AI tools"

    Tools without hook support still work with skills, commands, and agent docs - they just won't get automatic session-start context injection. See [Session Hooks](development/session-hooks.md) for which tools are supported and how to add more.

## Project structure

```
workspace/
├── .ai-workspace/         # Infrastructure (scripts, templates, config)
├── agent-docs/            # Documentation modules for AI agents
├── commands/              # Cross-tool AI commands (/command-name)
├── skills/                # Agent skills (SKILL.md files)
├── repositories/          # Git submodules (your projects)
├── .tmp/                  # Git-ignored directory for agent work artifacts
├── agent-tools.yaml       # CLI tool definitions for discovery
├── ai-workspace.toml      # Workspace configuration
├── AGENTS.md              # Auto-generated (do not edit directly)
└── AGENTS.project.md      # Your agent instructions (merged into AGENTS.md)
```

## Design principles

- **Model agnostic** - Works with any AI model or tool. No vendor lock-in.
- **Context-rich** - Agents get repo status, tool availability, and docs for autonomous work.
- **Fully automated** - Pre-commit validates, session hooks inject context. No manual steps.
- **Efficient** - Modular docs keep token usage low. Agents load only what's relevant.
- **Cross-tool** - One source of truth, distributed to multiple tool directories.

## Quick links

- [Getting Started](getting-started.md) - Set up your workspace
- [Repositories](repositories.md) - Submodule model and status reporting
- [Configuration](configuration.md) - Configure `ai-workspace.toml`
