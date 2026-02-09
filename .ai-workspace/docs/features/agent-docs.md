# Agent Docs

Agent Docs are modular, task-focused documentation files optimized for AI agent consumption. They provide context and instructions that agents read when performing specific tasks - and skip when they're not relevant.

## Why agent docs?

AI agents work best with focused context. Dumping everything into a single giant document wastes tokens and confuses models. Agent Docs solve this by:

- Letting agents **discover** what documentation exists via short metadata
- Letting agents **select** only the docs relevant to their current task
- Keeping each doc **self-contained** so agents don't need to chase cross-references

## Agent Docs vs. Skills

This workspace also supports [Agent Skills](skills.md), the industry standard for packaging agent capabilities. So why maintain a separate system for documentation?

**Skills** are designed for broad use cases and rely on each AI tool's built-in activation logic. The agent matches a skill's `description` against the current request to decide relevance - and often decides it isn't relevant.

**Agent Docs** are more forceful. In the generated `AGENTS.md`, reading relevant docs is **Critical Requirement #1**:

- Agents must review the full listing before starting any task
- Each doc has a dedicated `when` field with explicit triggering conditions
- The workspace controls this workflow via the `AGENTS.md` template, rather than relying on each AI tool's opaque skill activation
- The format is lighter: just a markdown file with three frontmatter fields, no directory structure or scripts required

!!! info ""

    Vercel's [agent evaluations](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) found that a docs index embedded in AGENTS.md (with agents retrieving full docs on demand) achieved 100% task success - compared to 79% with skills using explicit instructions, and 53% with default skill activation.

**In short:** Use Agent Docs for project knowledge agents should always consider. Use Skills for reusable workflows and capabilities agents invoke for specific tasks.

## How it works

1. **You write docs** in `agent-docs/` with YAML frontmatter (`title`, `description`, `when`)
2. **Pre-commit generates** a listing in `AGENTS.md` from the frontmatter
3. **Agents review** the listing at task start and read docs relevant to their task
4. **Agents load** the full document content only when needed

This means you can have dozens of docs without bloating the agent's context - they only load what they need.

In `AGENTS.md`, the generated listing uses XML for structured parsing:

```xml
<agent-docs-items>
  <doc path="agent-docs/database-migrations.md">
    <name>Database Migrations Guide</name>
    <description>How to create, run, and troubleshoot database migrations...</description>
    <when-to-read>When modifying database schema, debugging migration failures...</when-to-read>
  </doc>
</agent-docs-items>
```

## Directory structure

Both flat files and subdirectories are supported:

```
agent-docs/
├── README.md              # Guidelines (excluded from docs list)
├── api-authentication.md  # Flat file
├── database-migrations.md # Flat file
└── guides/                # Subdirectory for organization
    ├── deploy-guide.md
    └── setup-guide.md
```

All `.md` files (except `README.md`) with valid frontmatter are automatically discovered, regardless of nesting depth.

## Creating a document

### 1. Create the file

Create a `.md` file in `agent-docs/` (or a subdirectory for organization).

### 2. Add frontmatter

Every agent doc needs YAML frontmatter with three required fields:

```yaml
---
title: My Documentation Title
description: |
  What this doc covers and what problems it solves.
  Focus on use cases, not a table of contents.
when: |
  When performing X tasks or encountering Y situations.
  Be specific about triggering conditions.
---
```

`title`
:   Human-readable title for the doc

`description`
:   What problems this doc solves (helps agents decide relevance)

`when`
:   Triggering conditions - tasks, errors, decisions where this helps

!!! tip "Frontmatter tip"

    Frontmatter helps agents decide **"Should I read this?"** - not **"What's in this?"**.  
    Focus on use cases and triggering conditions, not content inventories.

### 3. Write the content

Start with a heading matching your title, then write the documentation. See the [complete example](#complete-example) below.

### 4. Run pre-commit

After creating or updating a doc, run pre-commit to update `AGENTS.md`:

```bash
uv run pre-commit run --all-files
```

The listing in `AGENTS.md` is automatically regenerated from your frontmatter.

## Writing and maintaining docs

- **Accuracy first** - Verify facts by reading source code. Inaccurate docs cause agents to fail tasks.
- **Token efficiency** - Be concise but complete. Every sentence should provide value.
- **Focused scope** - One topic per document. If it grows too broad, split into multiple docs.
- **Self-contained** - Don't reference other agent-docs. Each doc should stand alone.
- **Generic examples** - Use placeholders (`<version>`, `<collection-name>`) instead of specific versions that will become outdated.
- **Actionable content** - Include file paths, command examples, and decision trees. Theory without action isn't useful.
- **Scannable structure** - Use clear hierarchical headings (H2/H3). Agents locate information by scanning headings.
- **Update content** when implementation changes.
- **Update frontmatter** when the doc addresses new use cases not covered by the existing description.
- **Skip metadata updates** when adding detail within areas the description already covers.

## Complete example

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

All API requests require authentication via one of three methods.

## JWT Tokens

### Obtaining a Token

POST to `/auth/login` with email and password credentials.

### Token Structure

Tokens contain: user ID, roles, expiration time (1 hour default).

### Refreshing Tokens

Call `/auth/refresh` with a valid token before expiration.

## API Keys

For service-to-service communication. Generated in the admin panel.

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Missing/invalid token | Check Authorization header |
| 403 Forbidden | Valid token, insufficient permissions | Verify user roles |
```

## Disabling agent docs

To disable the agent-docs feature entirely:

```toml
[features]
agent_docs = false
```

!!! warning

    Disabling removes the `agent-docs/` directory only if it's empty or contains just a README. If it has user content, pre-commit will fail with instructions to remove files manually first.
