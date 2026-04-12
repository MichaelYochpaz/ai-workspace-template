#!/usr/bin/env python3
"""Session-start orchestrator for AI tool hooks.

Runs at the start of AI tool sessions and collects context from multiple
sources into a unified output.

Supports two output modes:
  - Plain text (default): For tools that capture stdout directly
  - JSON (--tool <name>): For tools that require a JSON hook protocol
    Each tool's JSON schema is defined in FORMATTERS.

Adding a new tool: add an entry to FORMATTERS and create the tool's config file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from session_context import SessionContext

# Import session-start tasks
from repository_status import run_repository_status
from tool_discovery import run_tool_discovery

# JSON output formatters for tools that use a JSON hook protocol.
# Each formatter receives the rendered context string and returns a dict
# matching the tool's expected sessionStart output schema.
FORMATTERS: dict[str, Any] = {
    "claude": lambda ctx: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}},
    "codex": lambda ctx: {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": ctx,
        }
    },
    "cursor": lambda ctx: {"additional_context": ctx},
    "gemini": lambda ctx: {"hookSpecificOutput": {"additionalContext": ctx}},
}

# Maximum character count for hook output, per tool.
# Tools with known caps should be listed here so the rendered context
# is truncated gracefully instead of being replaced with a file preview.
# Claude Code caps injected hook output (additionalContext / stdout) at
# 10,000 characters; we use 9,500 to leave headroom for minor overhead.
OUTPUT_LIMITS: dict[str, int] = {
    "claude": 9500,
    # codex: no documented output limit as of 2026-04 (hooks are experimental)
}


def collect_context(max_chars: int | None = None) -> str:
    """Run all session-start tasks and return the rendered context.

    Args:
        max_chars: Maximum character count for the output. Passed to
            SessionContext.render() to truncate gracefully when a tool
            has a known output size cap. None means no limit.
    """
    ctx = SessionContext()

    # Get repository root (scripts are in .ai-workspace/scripts/)
    repo_root = Path(__file__).parent.parent.parent

    # Gather repository status for agent context
    run_repository_status(ctx, repo_root)

    # Run tool discovery
    run_tool_discovery(ctx, repo_root)

    return ctx.render(max_chars=max_chars)


def main() -> None:
    """Run session-start tasks and output context in the requested format."""
    parser = argparse.ArgumentParser(description="Session-start context collector")
    parser.add_argument(
        "--tool",
        choices=FORMATTERS,
        help="Output JSON in the specified tool's hook format. "
        "Without this flag, outputs plain text.",
    )
    args = parser.parse_args()

    # Tools with JSON protocols send input on stdin; consume it so the
    # process doesn't hang.
    if args.tool:
        sys.stdin.read()

    output = collect_context(
        max_chars=OUTPUT_LIMITS.get(args.tool) if args.tool else None
    )

    if args.tool:
        response = FORMATTERS[args.tool](output) if output else {}
        json.dump(response, sys.stdout)
    else:
        if output:
            print(output)


if __name__ == "__main__":
    main()
