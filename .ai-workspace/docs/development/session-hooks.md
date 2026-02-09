# Session Hooks

Session hooks inject context into AI agents at the start of a session. Instead of agents starting cold, they immediately know which repos exist, what state they're in, and which CLI tools are available.

## How it works

The session-start script (`.ai-workspace/scripts/session-start.py`) runs two tasks:

1. **Repository status** - Reports each submodule's branch, uncommitted changes, and how far behind remote
2. **Tool discovery** - Detects installed CLI tools and injects usage instructions (see [Tool Discovery](../features/tool-discovery.md))

The output is wrapped in `<session-context>` XML tags that agents consume automatically.

## Supported tools

Hook configurations are committed to the repo and work out of the box for these tools:

| Tool | Config location |
|------|----------------|
| **Claude Code** | `.claude/settings.json` |
| **OpenCode** | `.opencode/plugins/session-sync.ts` |
| **Cursor** | `.cursor/hooks.json` |
| **Gemini CLI** | `.gemini/settings.json` |

!!! info "Other AI tools"

    Tools without hook support still work with skills, commands, and agent docs - they just won't get automatic session-start context injection.

## Output modes

The session-start script supports two output modes:

**Plain text** (default) - For tools that capture stdout directly (Claude Code, OpenCode). Run with no arguments:

```bash
uv run .ai-workspace/scripts/session-start.py
```

**JSON** (`--tool <name>`) - For tools that require a JSON hook protocol (Cursor, Gemini CLI). Each tool has its own expected JSON schema:

```bash
echo '{}' | uv run .ai-workspace/scripts/session-start.py --tool cursor
echo '{}' | uv run .ai-workspace/scripts/session-start.py --tool gemini
```

JSON modes require stdin input because the tools send JSON that the script consumes. Pipe `echo '{}'` when testing manually.

## Adding support for a new tool

If an AI tool supports session-start hooks with a JSON protocol, two steps are needed:

### 1. Add a formatter

Open `.ai-workspace/scripts/session-start.py` and add an entry to the `FORMATTERS` dict, matching the tool's expected output schema:

```python
FORMATTERS = {
    "cursor": lambda ctx: {"additional_context": ctx},
    "gemini": lambda ctx: {"hookSpecificOutput": {"additionalContext": ctx}},
    "newtool": lambda ctx: {"context": ctx},  # Match the tool's schema
}
```

### 2. Create the tool's config file

Create the hook config in the tool's expected location, pointing to the script:

```
uv run .ai-workspace/scripts/session-start.py --tool newtool
```

The exact config format depends on the tool - refer to its hooks documentation for the file location, structure, and available options.

If the tool captures stdout as plain text (no JSON protocol), skip step 1 and call the script with no arguments.

## Limitations

- Session hooks produce a **point-in-time snapshot**. The script runs at specific lifecycle points (e.g., session start, resume) and the output remains static until the next execution. Between runs, the injected context does not update when the underlying state changes.

- **Stale repository status.** If repo state changes after the last hook execution (branches switched externally, new commits pushed by others, or changes made by parallel agents), the injected context no longer reflects reality. Agents are instructed to verify repo state with git commands before branch switches or destructive operations.

- **Resume behavior varies by tool.** Some tools re-run hooks when resuming a session (Claude Code and Gemini CLI, via `"matcher": "startup|resume"` in their hook configs). Others may serve the original cached output. If a tool's hook config does not specify resume behavior, the agent may start a resumed session with outdated context.

- **Parallel agents on a shared workspace.** Multiple agents operating on the same workspace can cause race conditions — one agent may switch a branch while another still operates based on the original session-start context. This is a fundamental limitation of shared-filesystem concurrency, not specific to this workspace.
