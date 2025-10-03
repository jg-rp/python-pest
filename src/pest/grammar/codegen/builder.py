"""Utilities for building indented Python source code as strings."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pest.grammar.rule import Rule


class Builder:
    """Utility class for building indented Python source code as strings.

    The Builder accumulates lines of code, manages indentation levels,
    and provides helpers for generating temporary variable names and
    rendering the final code as a string.
    """

    def __init__(self, rules: dict[str, Rule] | None = None) -> None:
        """Initialize a new Builder with empty code and zero indentation."""
        self.lines: list[str] = []
        self.indent = 0
        self.counter = 0
        self.module_constants: list[tuple[str, str]] = []
        self.rule_constants: list[tuple[str, str]] = []
        self.rules = rules

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

    def constant(self, prefix: str, expr: str, *, rule_scope: bool = True) -> str:
        """Register a new constant and return its name.

        Args:
            prefix: Prefix for the constant variable name.
            expr: The expression or value to assign to the constant.
            rule_scope: If True, the constant is scoped to the rule; otherwise, it is
                module-scoped.

        Returns:
            The name of the newly registered constant.
        """
        self.counter += 1
        name = f"{prefix}{self.counter}"
        if rule_scope:
            self.rule_constants.append((name, expr))
        else:
            self.module_constants.append((name, expr))
        return name
