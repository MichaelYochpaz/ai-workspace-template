# Skills

Reusable agent capabilities following the [Agent Skills specification](https://agentskills.io/specification). Skills are defined here and automatically distributed to tool-specific directories via symlinks.

## Creating a skill

### 1. Create the skill directory and SKILL.md

Create a directory under `skills/` with a `SKILL.md` file containing YAML frontmatter and instruction content:

```markdown
---
name: my-skill
description: What this skill does. Use when X, Y, or Z.
---

# My Skill

Step-by-step instructions for the agent...
```

### 2. Validate

```bash
uv run .ai-workspace/scripts/transpile-skills.py --validate
```

## Directory structure

```
skills/<skill-name>/
├── SKILL.md           # Required: frontmatter + instructions
├── scripts/           # Optional: executable scripts
├── references/        # Optional: additional documentation
└── assets/            # Optional: templates, data files
```

## Frontmatter requirements

`name` (required)
:   Must match directory name. Lowercase `a-z`, `0-9`, `-` only. Max 64 characters.

`description` (required)
:   Brief description of what the skill does and when to use it. Max 1024 characters.

The `SKILL.md` must also have body content (instructions) after the frontmatter.

## Validation and distribution

```bash
# Validate only (also runs on pre-commit)
uv run .ai-workspace/scripts/transpile-skills.py --validate

# Validate + distribute to configured target directories
uv run .ai-workspace/scripts/transpile-skills.py
```

Distribution creates symlinks from tool-specific directories (configured in `ai-workspace.toml` under `distribution.skills_paths`) to the source skill directory. Changes to the source are immediately reflected everywhere.

## Writing tips

- **Description is key** - Write descriptions that semantically match user requests. Include capabilities AND trigger conditions so agents activate the skill when appropriate.
- **Progressive disclosure** - Agents load `name` + `description` at startup (~100 tokens). Full `SKILL.md` loads only when activated. Keep descriptions concise and instructions detailed.
- **Scripts use PEP 723** - Use inline dependencies with `uv run` for zero-install execution.
