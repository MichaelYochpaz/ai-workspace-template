# Session Hooks

Session hooks inject context into AI agents at the start of a session. Instead of agents starting cold, they immediately know which repos exist, what state they're in, and which CLI tools are available.

## How it works

The session-start script (`.ai-workspace/scripts/session-start.py`) runs two tasks:

1. **Repository status** - Reports each submodule's branch, uncommitted changes, and how far behind remote
2. **Tool discovery** - Detects installed CLI tools and injects usage instructions (see [Tool Discovery](../features/tool-discovery.md))

The output is wrapped in `<session-context>` XML tags that agents consume automatically.

## Supported tools

Hook configurations are committed to the repo and work out of the box for these tools:

| Tool | Config location | Notes |
|------|----------------|-------|
| **Claude Code** | `.claude/settings.json` | |
| **Codex CLI** | `.codex/hooks.json` | Experimental; requires feature flag in `.codex/config.toml`. Windows support currently disabled by Codex. |
| **OpenCode** | `.opencode/plugins/session-sync.ts` | |
| **Cursor** | `.cursor/hooks.json` | |
| **Gemini CLI** | `.gemini/settings.json` | |

!!! info "Other AI tools"

    Tools without hook support still work with skills, commands, and agent docs - they just won't get automatic session-start context injection.

## Output modes

The session-start script supports two output modes:

**Plain text** (default) - For tools that capture stdout directly (OpenCode). Run with no arguments:

```bash
uv run .ai-workspace/scripts/session-start.py
```

**JSON** (`--tool <name>`) - For tools that require a JSON hook protocol (Claude Code, Codex CLI, Cursor, Gemini CLI). Each tool has its own expected JSON schema:

```bash
echo '{}' | uv run .ai-workspace/scripts/session-start.py --tool claude
echo '{}' | uv run .ai-workspace/scripts/session-start.py --tool codex
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
    "claude": lambda ctx: {"hookSpecificOutput": {"additionalContext": ctx}},
    "codex": lambda ctx: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}},
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

- **Resume behavior varies by tool.** Some tools re-run hooks when resuming a session (Claude Code, Codex CLI, and Gemini CLI include `resume` in their hook matchers). Others may serve the original cached output. If a tool's hook config does not specify resume behavior, the agent may start a resumed session with outdated context.

- **Parallel agents on a shared workspace.** Multiple agents operating on the same workspace can cause race conditions — one agent may switch a branch while another still operates based on the original session-start context. This is a fundamental limitation of shared-filesystem concurrency, not specific to this workspace.

## Output size limits

Some tools cap the size of hook output injected into context. When the rendered session context exceeds a tool's limit, the tool may replace the full output with a truncated preview and a file path — losing the structured context the agent needs.

To handle this gracefully, `SessionContext.render()` accepts a `max_chars` parameter. When set, it drops sections from the end and appends a truncation notice instead of exceeding the limit. Per-tool limits are defined in the `OUTPUT_LIMITS` dict in `session-start.py`.

Currently known limits:

| Tool | Limit | Source |
|------|-------|--------|
| **Claude Code** | 10,000 chars (9,500 used) | [Hooks reference](https://code.claude.com/docs/en/hooks) |

When adding a new tool, check its documentation for output size constraints and add an entry to `OUTPUT_LIMITS` if applicable.

## Evaluated and deferred hooks

The following hook events were evaluated and intentionally deferred. This section exists to prevent re-evaluation without the original context.

### CwdChanged

**What it would do:** Inject submodule-specific context (e.g., AGENTS.md path, git status) when Claude changes into a submodule directory.

**Why deferred:**

- Fires on every `cd`, including transient directory changes for file reads — not just meaningful submodule transitions.
- AGENTS.md already instructs agents to verify repo state and read submodule docs before taking action, covering this need via static instructions.
- In a template repo, submodule layouts vary per instantiation. Detecting submodule boundaries requires path pattern maintenance that doesn't generalize.
- Executing `uv run` on every directory change adds noticeable latency for interactive use.

**Reconsider when:** Stale context causes recurring, documented failures that static instructions don't prevent.

### FileChanged (for ai-workspace.toml)

**What it would do:** Watch the workspace config file and warn Claude when it drifts from aligned state, suggesting to re-run the alignment script.

**Why deferred:**

- This file changes rarely and only by deliberate user action. The user who edits their own config doesn't need a hook reminder.
- The pre-commit hooks already catch alignment drift before commits are finalized.
- `FileChanged` fires on any matching file change, including edits Claude itself makes, creating a noisy feedback loop.

**Reconsider when:** Users report committing unaligned state despite pre-commit checks, or if the workspace gains config files that change more frequently.

### InstructionsLoaded

**What it would do:** Inject additional context when CLAUDE.md or `.claude/rules/*.md` files are loaded into context.

**Why deferred:**

- No concrete use case identified. The event is primarily diagnostic.
- AGENTS.md and session-start context already cover the instruction injection use case.
- Adding a second context injection path increases maintenance without clear benefit.

**Reconsider when:** A specific need arises to augment loaded instructions dynamically (e.g., injecting environment-specific overrides).

### PreToolUse (for git submodule safety)

**What it would do:** Intercept `git push`, `git submodule update --remote`, and `git pull --recurse-submodules` to enforce submodule workflow rules already documented in AGENTS.md.

**Why deferred:**

- Parsing git commands from bash invocations is fragile (quoted arguments, aliases, scripts that wrap git).
- AGENTS.md already documents these rules and agents generally follow them.
- The `if` field filter (e.g., `"Bash(git submodule update*)"`) mitigates latency but the stability of this syntax in a template repo is uncertain.
- Adding enforcement hooks for rules that are already followed creates overhead without proportional benefit.

**Reconsider when:** Agents repeatedly violate submodule workflow rules despite AGENTS.md instructions, or when the `PreToolUse` `if` syntax is well-documented and stable across Claude Code versions.
