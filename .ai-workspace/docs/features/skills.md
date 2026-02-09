# Skills

Different AI tools look for skills in different directories. This workspace lets you maintain skills in one place (`skills/`) and automatically distributes them to the right locations via symlinks.

Skills follow the [Agent Skills specification](https://agentskills.io/specification). See the spec for details on how to write them.

## What this workspace does

1. **Single source of truth** - You write skills in `skills/<name>/SKILL.md`
2. **Validation** - The transpile script validates frontmatter (required fields, name format, description length)
3. **Distribution** - Skills are symlinked to tool-specific directories so each tool discovers them natively
4. **Pre-commit integration** - Validation runs automatically on every commit

## Directory structure

```
skills/
└── <skill-name>/
    ├── SKILL.md           # Required: frontmatter + instructions
    ├── scripts/           # Optional: executable scripts
    ├── tests/             # Optional: test files
    ├── references/        # Optional: detailed documentation
    └── assets/            # Optional: templates, data files
```

## Validation rules

The transpile script (`transpile-skills.py`) validates each `SKILL.md`:

- **`name`** (required) - Must match directory name. Lowercase `a-z`, `0-9`, `-` only. Max 64 chars.
- **`description`** (required) - Max 1024 chars.
- **Body content** - SKILL.md must have content after the frontmatter, not just metadata.

## Distribution

Skills in `skills/` are symlinked to tool-specific directories:

```bash
# Validate + distribute
uv run .ai-workspace/scripts/transpile-skills.py

# Validate only (used by pre-commit)
uv run .ai-workspace/scripts/transpile-skills.py --validate
```

Distribution creates **symlinks** from tool-specific directories to the source skill directory. Changes to the source are immediately reflected everywhere.

### Where skills are distributed

Skills are symlinked to every path listed under `skills_paths` in `ai-workspace.toml`. Some tools discover skills natively from `skills/` and don't need a distribution entry.

```toml
[distribution]
skills_paths = [".opencode/skill"]
```

See [Configuration](../configuration.md#distribution) for the full reference.

## Learn more

- [Agent Skills Specification](https://agentskills.io/specification) - How to write skills
- [Agent Skills Website](https://agentskills.io) - Community resources and examples
