"""Parser generator state."""

from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING
from typing import Iterator

if TYPE_CHECKING:
    from pest.grammar.expression import Expression
    from pest.grammar.expression import Success

    from .parser import Parser


class ParserState:
    """Holds parsing state.

    Includes input string, current parsing context, and a stack for stateful
    grammar operations.
    """

    __slots__ = ("parser", "input", "atomic_depth", "stack", "cache")

    def __init__(self, parser: Parser, input_: str) -> None:
        self.parser = parser
        self.input = input_
        self.atomic_depth = 0
        self.stack: list[str] = field(default_factory=list)
        self.cache: dict[tuple[int, Expression], list[Success] | None] = {}

    def memoized_parse(self, expr: Expression, pos: int) -> Iterator[Success]:
        """Parse `expr` or return a cached parse result."""
        key = (pos, expr)
        if key in self.cache:
            cached = self.cache[key]
            if cached is not None:
                yield from cached
            return

        results = list(expr.parse(self, pos))
        self.cache[key] = results if results else None
        yield from results

    def parse_implicit_rules(self, pos: int) -> Iterator[Success]:
        """Parse any implicit rules (`WHITESPACE` and `COMMENT`) starting at `pos`.

        Returns a list of ParseResult instances. Each result represents one
        successful application of an implicit rule. `node` will be None if
        the rule was silent.
        """
        if self.atomic_depth > 0:
            return

        # TODO: combine and cache whitespace and comment rules in to one?
        whitespace_rule = self.parser.rules.get("WHITESPACE")
        comment_rule = self.parser.rules.get("COMMENT")

        if not whitespace_rule and not comment_rule:
            return

        while True:
            new_pos = pos
            matched = False

            if whitespace_rule:
                for result in whitespace_rule.parse(self, new_pos):
                    matched = True
                    new_pos = result.pos
                    if result.pair:
                        yield result

            if comment_rule:
                for result in comment_rule.parse(self, new_pos):
                    matched = True
                    new_pos = result.pos
                    if result.pair:
                        yield result

            if not matched:
                break

            pos = new_pos

    def push(self, value: str) -> None:
        """Push a value onto the stack."""
        self.stack.append(value)

    def drop(self, n: int = 1) -> None:
        """Drop the top `n` values from the stack."""
        if n > len(self.stack):
            raise IndexError("Cannot drop more elements than present in stack")
        del self.stack[-n:]

    def peek(self) -> str | None:
        """Peek at the top element of the stack.

        Returns:
            The top value, or None if the stack is empty.
        """
        return self.stack[-1] if self.stack else None

    def peek_slice(self, start: int | None = None, end: int | None = None) -> list[str]:
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
