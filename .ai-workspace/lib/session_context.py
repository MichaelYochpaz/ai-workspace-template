#!/usr/bin/env python3
"""Session context collector for session-start hooks.

Collects named sections from multiple sources and outputs them
wrapped in <session-context> tags for LLM consumption.
"""

from __future__ import annotations


class SessionContext:
    """Collects named content sections and outputs them as unified context."""

    def __init__(self) -> None:
        self._sections: list[tuple[str, str]] = []

    def add_section(self, name: str, content: str) -> None:
        """Add a named section. Empty content is silently ignored."""
        content = content.strip()
        if content:
            self._sections.append((name, content))

    def render(self) -> str:
        """Return all sections wrapped in <session-context> tags.

        Returns empty string if no sections have content.
        """
        if not self._sections:
            return ""

        parts = ["<session-context>"]
        for _name, content in self._sections:
            parts.append(content)
        parts.append("</session-context>")
        return "\n\n".join(parts)

    def print(self) -> None:
        """Print all sections wrapped in <session-context> tags.

        Outputs nothing if no sections have content.
        """
        output = self.render()
        if output:
            print(output)
