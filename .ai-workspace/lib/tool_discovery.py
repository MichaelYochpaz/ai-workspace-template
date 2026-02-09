#!/usr/bin/env python3
"""Tool discovery for session-start hooks.

Detects installed CLI tools defined in agent-tools.yaml and injects
their availability and usage instructions into the session context.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from config import load_config

if TYPE_CHECKING:
    from session_context import SessionContext


def _load_tools(repo_root: Path) -> dict[str, Any]:
    """Load tool definitions from agent-tools.yaml."""
    tools_path = repo_root / "agent-tools.yaml"
    if not tools_path.exists():
        return {}

    try:
        with open(tools_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError:
        return {}


def _format_text_block(tag: str, text: str, indent: str = "  ") -> str:
    """Format a multi-line text value as an indented XML element."""
    lines = text.strip().splitlines()
    if not lines:
        return ""
    inner = "\n".join(f"{indent}  {line}" for line in lines)
    return f"{indent}<{tag}>\n{inner}\n{indent}</{tag}>"


def _build_tool_xml(tool_id: str, tool: dict[str, Any], available: bool) -> str:
    """Build XML for a single tool entry."""
    name = tool.get("name", tool_id)
    description = tool.get("description", "")
    when_to_use = tool.get("when_to_use", "")
    instructions = tool.get("instructions", "")

    if not available:
        return f'  <tool id="{tool_id}" available="false">\n    <name>{name}</name>\n    <description>{description}</description>\n  </tool>'

    parts = [f'  <tool id="{tool_id}">']
    parts.append(f"    <name>{name}</name>")
    parts.append(f"    <description>{description}</description>")

    if when_to_use:
        parts.append(_format_text_block("when-to-use", when_to_use, "    "))

    if instructions:
        parts.append(_format_text_block("instructions", instructions, "    "))

    parts.append("  </tool>")
    return "\n".join(parts)


def run_tool_discovery(ctx: SessionContext, repo_root: Path) -> None:
    """Discover available CLI tools and add to session context.

    Reads tool definitions from agent-tools.yaml, checks each tool's
    command on PATH, and formats the results as XML.
    """
    tools = _load_tools(repo_root)
    if not tools:
        return

    config = load_config(repo_root / "ai-workspace.toml")
    show_unavailable = config.tools.show_unavailable

    entries: list[str] = []

    for tool_id in sorted(tools):
        tool = tools[tool_id]
        if not isinstance(tool, dict):
            continue

        command = tool.get("command")
        if not command:
            continue

        available = shutil.which(command) is not None

        if available or show_unavailable:
            entries.append(_build_tool_xml(tool_id, tool, available))

    if entries:
        content = "<available-tools>\n" + "\n".join(entries) + "\n</available-tools>"
        ctx.add_section("available-tools", content)
