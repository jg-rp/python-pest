"""Utilities for building indented Python source code as strings."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


class Builder:
    """Utility class for building indented Python source code as strings.

    The Builder accumulates lines of code, manages indentation levels,
    and provides helpers for generating temporary variable names and
    rendering the final code as a string.
    """

    def __init__(self) -> None:
        """Initialize a new Builder with empty code and zero indentation."""
        self.lines: list[str] = []
        self.indent = 0
        self.counter = 0
        self.module_constants: list[tuple[str, str]] = []
        self.rule_constants: list[tuple[str, str]] = []

    def writeln(self, line: str = "") -> None:
        """Append a line to the code, respecting the current indentation level.

        Args:
            line: The line of code to append. Indentation is automatically applied.
        """
        self.lines.append("    " * self.indent + line)

    @contextmanager
    def block(self) -> Iterator[Builder]:
        """Context manager to increase indentation for a block of code.

        Usage:
            with builder.block():
                builder.writeln("indented line")
        """
        self.indent += 1
        yield self
        self.indent -= 1

    def new_temp(self, prefix: str = "_tmp") -> str:
        """Generate a new unique temporary variable name.

        Args:
            prefix: Prefix for the temporary variable name.

        Returns:
            A unique variable name as a string.
        """
        self.counter += 1
        return f"{prefix}{self.counter}"

    def render(self) -> str:
        """Render the accumulated code as a single string.

        Returns:
            The complete source code as a string.
        """
        return "\n".join(self.lines)

    def constant(self, prefix: str, line: str, *, rule_scope: bool = True) -> str:
        """Register a new constant and return its name."""
        self.counter += 1
        name = f"{prefix}{self.counter}"
        if rule_scope:
            self.rule_constants.append((name, line))
        else:
            self.module_constants.append((name, line))
        return name

    def render_constants(self, *, rule_scope: bool = True) -> list[str]:
        """"""
        if rule_scope:
            return [f"{name} = {line}" for name, line in self.rule_constants]
        return [f"{name} = {line}" for name, line in self.module_constants]
