# AI Workspace Infrastructure

This directory contains the infrastructure for the AI Workspace Template.

**Full documentation:** [Configuration Reference](https://michaelyochpaz.github.io/ai-workspace-template/configuration/)

## Directory Structure

```
.ai-workspace/
├── docs/                  # Documentation source (Zensical site)
├── lib/                   # Python library (config models)
├── scripts/               # Automation scripts
├── templates/             # Jinja2 templates
└── zensical.toml          # Documentation site config
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `setup.py` | One-time workspace setup (submodules, hooks, alignment) |
| `align-workspace.py` | Pre-commit: regenerates AGENTS.md, manages feature dirs |
| `session-start.py` | Session start: reports repo status, discovers tools |
| `transpile-skills.py` | Validates and distributes skills |
| `transpile-commands.py` | Validates and distributes commands |
| `mktmpdir.py` | Creates unique task directories under `.tmp/` |

## AGENTS.md Generation

`AGENTS.md` is auto-generated from `templates/AGENTS.md.j2`. Don't edit directly.

- **Workspace instructions:** Edit `templates/AGENTS.md.j2`
- **Project-specific instructions:** Edit `AGENTS.project.md` at repo root

Regenerate manually:
```bash
uv run .ai-workspace/scripts/align-workspace.py
```

## Configuration

The workspace is configured via `ai-workspace.toml` at the repository root. Key sections:

| Section | Purpose |
|---------|---------|
| `[repositories]` | Repository status and sync settings |
| `[features]` | Enable/disable skills, commands, agent-docs |
| `[tools]` | Tool discovery settings |
| `[distribution]` | Where to distribute skills/commands |

See [Configuration](https://michaelyochpaz.github.io/ai-workspace-template/configuration/) for the full reference.

## Documentation Site

Built with [Zensical](https://zensical.org/). Config in `zensical.toml`.

```bash
# Preview locally
zensical serve --config-file .ai-workspace/zensical.toml

# Build static site
zensical build --config-file .ai-workspace/zensical.toml
```
