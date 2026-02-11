# Getting Started

## Prerequisites

- **Python 3.11+** - Required for workspace scripts
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
- **Git** - With submodule support (any recent version)

!!! tip "Installing uv"

    ```bash
    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows (PowerShell)
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Setup

### 1. Create your repository

Click **"Use this template"** on GitHub to create a new repository. This gives you a clean repo with the same directory structure and files, but with its own independent git history.

!!! note "Why not clone or fork?"

    **Cloning** gives you the template's full git history and a remote pointing to the original - that's not what you want for your own workspace.

    **Forking** is for contributing back to the template, not for building your own project on top of it.

    The **"Use this template"** button creates a fresh repo that's entirely yours.

### 2. Install dependencies and set up workspace

```bash
uv sync
uv run .ai-workspace/scripts/setup.py
```

This installs Python dependencies, initializes submodules, installs pre-commit hooks, and generates your initial `AGENTS.md`.

!!! note "What the setup script does"

    - Initializes git submodules (if any are configured)
    - Installs pre-commit hooks (automatically validates your workspace on every commit)
    - Validates the workspace and generates `AGENTS.md`

    The script is idempotent - safe to re-run at any time.

### 3. Add your repositories

Add repositories to the `repositories/` directory:

```bash
git submodule add <repository-url> repositories/<name>
```

For example:

```bash
git submodule add git@github.com:org/backend.git repositories/backend
git submodule add git@github.com:org/frontend.git repositories/frontend
```

See [Repositories](repositories.md) for branch tracking, commit workflow, and troubleshooting.

## Customizing your workspace

### Edit your agent instructions

Open `AGENTS.project.md` at the repo root. This is where you write your own instructions and context for AI agents - the same kind of content you'd normally put in an `AGENTS.md` file. It gets merged into the auto-generated `AGENTS.md` when running pre-commit.

```markdown
## Project Overview
Brief description of what this project does.

## Key Concepts
- **Term 1** - Definition
- **Term 2** - Definition

## Repository Structure
- `repositories/backend/` - Go API server
- `repositories/frontend/` - React web app
```

Remove the `<placeholder>` tags when adding your content. See [AGENTS.md Generation](agents-md.md) for how the template system works.

### Configure the workspace

Edit `ai-workspace.toml` to enable/disable features and configure distribution paths. See [Configuration](configuration.md) for the full reference.

### Add agent documentation

Create focused docs in `agent-docs/` that agents read when tasks match. See [Agent Docs](features/agent-docs.md).

### Define CLI tools

Edit `agent-tools.yaml` to define CLI tools your team uses. These are auto-detected at session start and injected into agent context (for tools with [hook support](index.md#session-hooks)). See [Tool Discovery](features/tool-discovery.md).

## Important: AGENTS.md is auto-generated

!!! warning "Do not edit AGENTS.md directly"

    `AGENTS.md` is regenerated from templates on every pre-commit run. Any manual edits will be overwritten.

    - **Your instructions** - Edit `AGENTS.project.md` at the repo root
    - **Template structure** - Edit `.ai-workspace/templates/AGENTS.md.j2` (advanced)

    If `AGENTS.md` gets out of sync (e.g., after editing config or agent-docs), running `uv run pre-commit run --all-files` will regenerate it. See [AGENTS.md Generation](agents-md.md) for details.

## Verifying your setup

Run the session-start script manually to verify everything works:

```bash
uv run .ai-workspace/scripts/session-start.py
```

Then run the alignment script and pre-commit to validate the workspace:

```bash
uv run .ai-workspace/scripts/align-workspace.py
uv run pre-commit run --all-files
```

If everything passes, your workspace is ready.

## Next steps

- [Repositories](repositories.md) - Submodule workflow and status reporting
- [Configuration](configuration.md) - Customize `ai-workspace.toml`
- [Agent Docs](features/agent-docs.md) - Write docs for AI agents
- [Skills](features/skills.md) - Distribute agent skills across tools
- [Commands](features/commands.md) - Distribute commands across tools
- [Tool Discovery](features/tool-discovery.md) - Set up CLI tool discovery
