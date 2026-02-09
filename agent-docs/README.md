# Agent Docs

Modular, task-focused documentation optimized for AI agent consumption. Agents selectively load docs based on task relevance, keeping context targeted and token usage low.

## Creating a document

### 1. Create the file with frontmatter

Create a `.md` file in this directory (or a subdirectory for organization) with three required YAML frontmatter fields:

```yaml
---
title: My Topic
description: |
  What this doc covers and what problems it solves.
  Focus on use cases, not a table of contents.
when: |
  When performing X tasks or encountering Y situations.
  Be specific about triggering conditions.
---
```

`title` - Human-readable title for the doc.

`description` - What problems this doc solves (helps agents decide relevance).

`when` - **Critical field.** Agents scan this at task start to decide whether to read the doc - vague conditions cause agents to skip it. Write specific triggers: task types, codebase areas, error scenarios. Include a few illustrative examples (file paths, error messages) to aid matching, but frame them as examples so agents don't dismiss the doc when their exact case isn't listed.

**Weak** (too vague - agents can't match this to concrete tasks):
```yaml
when: When working with the API.
```

**Strong** (specific conditions with illustrative examples):
```yaml
when: |
  When modifying API authentication or authorization logic.
  When debugging 401/403 errors or token expiration issues.
  When adding new endpoints that require auth (e.g., middleware
  configuration, role-based access checks).
```

### 2. Write the content

Start with a heading matching your title, then write the documentation:

```markdown
---
title: API Authentication Guide
description: |
  How authentication works in the API layer.
  Covers JWT tokens, API keys, and OAuth flows.
when: |
  When implementing auth-related features, debugging 401/403 errors,
  or understanding how requests are authenticated.
---

# API Authentication Guide

## Overview

All API requests require authentication via one of three methods...
```

### 3. Run pre-commit

After creating or updating a doc, run pre-commit to update the listing in `AGENTS.md`:

```bash
uv run pre-commit run --all-files
```

## Directory structure

Both flat files and subdirectories are supported:

```
agent-docs/
├── README.md              # This file (excluded from docs list)
├── simple-topic.md        # Flat file
└── guides/                # Or use subdirectories
    └── setup-guide.md
```

All `.md` files (except `README.md`) with valid frontmatter are automatically discovered, regardless of nesting depth.

## How it works

1. You write docs here with YAML frontmatter (`title`, `description`, `when`)
2. Pre-commit generates a listing in `AGENTS.md` from the frontmatter
3. Agents review the listing at task start and read docs relevant to their task
4. Agents load the full document content only when needed

This means you can have dozens of docs without bloating the agent's context.

## Writing guidelines

- **Accuracy first** - Verify facts by reading source code. Inaccurate docs cause agents to fail tasks.
- **Focused scope** - One topic per document. If it grows too broad, split into multiple docs.
- **Prefer self-contained docs** - Minimize cross-references to other agent-docs. Each doc the agent reads should ideally provide complete context without requiring additional docs to be loaded.
- **Actionable content** - Include file paths, command examples, and decision trees. Theory without action isn't useful.
- **Token efficiency** - Be concise but complete. Every sentence should provide value.
- **Generic examples** - Use placeholders (`<version>`, `<name>`) instead of specific values that will become outdated.
- **Scannable structure** - Use clear hierarchical headings (H2/H3). Agents locate information by scanning headings.
