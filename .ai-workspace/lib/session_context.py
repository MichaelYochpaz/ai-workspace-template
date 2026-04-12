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

    def render(self, max_chars: int | None = None) -> str:
        """Return all sections wrapped in <session-context> tags.

        Args:
            max_chars: Maximum character count for the output. If the
                rendered output exceeds this limit, sections are dropped
                from the end until it fits, with a truncation notice.
                None means no limit.

        Returns empty string if no sections have content.
        """
        if not self._sections:
            return ""

        parts = ["<session-context>"]
        for _name, content in self._sections:
            parts.append(content)
        parts.append("</session-context>")
        output = "\n\n".join(parts)

        if max_chars is None or len(output) <= max_chars:
            return output

        # Drop sections from the end until within limit
        truncation_notice = (
            "(Session context truncated due to output size limit. "
            "{dropped} of {total} sections omitted.)"
        )
        total = len(self._sections)
        sections = list(self._sections)
        while sections:
            sections.pop()
            dropped = total - len(sections)
            notice = truncation_notice.format(dropped=dropped, total=total)
            parts = ["<session-context>"]
            for _name, content in sections:
                parts.append(content)
            parts.append(notice)
            parts.append("</session-context>")
            candidate = "\n\n".join(parts)
            if len(candidate) <= max_chars:
                return candidate

        # Nothing fits — return just the notice
        notice = truncation_notice.format(dropped=total, total=total)
        return f"<session-context>\n\n{notice}\n\n</session-context>"

    def print(self) -> None:
        """Print all sections wrapped in <session-context> tags.

        Outputs nothing if no sections have content.
        """
        output = self.render()
        if output:
            print(output)
