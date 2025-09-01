"""Parser generator state."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pest.result import ParseResult

    from .grammar import Grammar


@dataclass(slots=True)
class ParserState:
    """Holds parsing state.

    Includes input string, current parsing context, and a stack for stateful
    grammar operations.
    """

    input: str
    grammar: Grammar
    atomic_depth: int = 0
    stack: list[object] = field(default_factory=list)

    def parse_implicit_rules(self, pos: int) -> list[ParseResult]:
        """Parse any implicit rules (`WHITESPACE` and `COMMENT`) starting at `pos`.

        Returns a list of ParseResult instances. Each result represents one
        successful application of an implicit rule. `node` will be None if
        the rule was silent.
        """
        if self.atomic_depth > 0:
            return []

        results: list[ParseResult] = []
        whitespace_rule = self.grammar.rules.get("WHITESPACE")
        comment_rule = self.grammar.rules.get("COMMENT")

        if not whitespace_rule and not comment_rule:
            return []

        while True:
            new_pos = pos
            matched = False

            if whitespace_rule:
                result = whitespace_rule.parse(self, new_pos)
                if result is not None:
                    results.append(result)
                    new_pos = result.pos
                    matched = True

            if comment_rule:
                result = comment_rule.parse(self, new_pos)
                if result is not None:
                    results.append(result)
                    new_pos = result.pos
                    matched = True

            if not matched:
                break

            pos = new_pos

        return results

    def push(self, value: object) -> None:
        """Push a value onto the stack."""
        self.stack.append(value)

    def drop(self, n: int = 1) -> None:
        """Drop the top `n` values from the stack."""
        if n > len(self.stack):
            raise IndexError("Cannot drop more elements than present in stack")
        del self.stack[-n:]

    def peek(self) -> object | None:
        """Peek at the top element of the stack.

        Returns:
            The top value, or None if the stack is empty.
        """
        return self.stack[-1] if self.stack else None

    def peek_slice(
        self, start: int | None = None, end: int | None = None
    ) -> list[object]:
        """Peek at a slice of the stack, similar to pest's `PEEK(start..end)`.

        Args:
            start: Start index of the slice (0 = bottom of stack).
            end:   End index of the slice (exclusive).

        Returns:
            A list of values from the stack slice. If no arguments are given,
            return the entire stack.

        Example:
            stack = [1, 2, 3, 4]
            peek_slice()         -> [1, 2, 3, 4]
            peek_slice(0, 2)     -> [1, 2]
            peek_slice(1, 3)     -> [2, 3]
            peek_slice(-2, None) -> [3, 4]
        """
        if start is None and end is None:
            return self.stack[:]
        return self.stack[slice(start, end)]
