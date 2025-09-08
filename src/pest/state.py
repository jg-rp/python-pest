"""Parser generator state."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from .grammar.expression import Success
from .grammar.expression import Terminal
from .grammar.expressions.rule import Rule

if TYPE_CHECKING:
    from pest.grammar.expression import Expression

    from .parser import Parser


class ParserState:
    """Holds parsing state.

    Includes input string, current parsing context, and a stack for stateful
    grammar operations.
    """

    __slots__ = (
        "parser",
        "input",
        "atomic_depth",
        "stack",
        "cache",
        "expr_stack",
        "failed_pos",
    )

    def __init__(self, parser: Parser, input_: str) -> None:
        self.parser = parser
        self.input = input_
        self.atomic_depth = 0
        self.stack: list[str] = []
        self.cache: dict[tuple[int, int], list[Success] | None] = {}
        self.expr_stack: list[tuple[Expression, int]] = []
        self.failed_pos: int = 0

    def parse(self, expr: Expression, pos: int) -> Iterator[Success]:
        """Parse `expr` or return a cached parse result."""
        key = (pos, id(expr))
        if key in self.cache:
            cached = self.cache[key]
            if cached is not None:
                yield from cached
            return

        self.expr_stack.append((expr, pos))
        results = list(expr.parse(self, pos))

        if results:
            self.cache[key] = results
            yield from results
            self.expr_stack.pop()
        else:
            if pos > self.failed_pos:
                self.failed_pos = pos
            self.cache[key] = None

    def failure_message(self) -> str:
        """Generate a human-readable error message for the furthest failure."""
        pos = self.failed_pos
        # TODO: better line break detection
        line = self.input.count("\n", 0, pos) + 1
        col = pos - self.input.rfind("\n", 0, pos)

        found = self.input[pos : pos + 10] or "end of input"

        # Walk stack to find relevant context
        rule = next(
            (e for e, _ in reversed(self.expr_stack) if isinstance(e, Rule)), None
        )

        non_terminal = next(
            (e for e, _ in reversed(self.expr_stack) if not isinstance(e, Terminal)),
            None,
        )

        expected = str(
            non_terminal
            or (self.expr_stack[-1][0] if self.expr_stack else "expression")
        )

        rule_str = f", in rule {rule.name}" if rule else ""
        return (
            f"error at {line}:{col}{rule_str}: expected {expected}, "
            f"found {found!r}{self._rule_tree_view()}"
        )

    def _rule_tree_view(self) -> str:
        if not self.expr_stack:
            return ""

        # unwind stack until we see a loop
        seen: set[tuple[Expression, int]] = set()
        unwound: list[tuple[Expression, int]] = []
        for expr, pos in self.expr_stack:
            key = (expr, pos)
            if key in seen:
                break  # loop detected
            seen.add(key)
            unwound.append((expr, pos))

        parts: list[str] = []
        indent = 0
        for expr, pos in unwound:
            if isinstance(expr, Rule):
                prefix = "  " * indent + f"- {expr.name}:{pos}"
                parts.append(prefix)
                indent += 1

        return "\n" + "\n".join(parts)

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
                for result in self.parse(whitespace_rule, new_pos):
                    matched = True
                    new_pos = result.pos
                    if result.pair and self.atomic_depth == 0:
                        yield result

            if comment_rule:
                for result in self.parse(comment_rule, new_pos):
                    matched = True
                    new_pos = result.pos
                    if result.pair and self.atomic_depth == 0:
                        yield result

            if not matched:
                yield Success(None, new_pos)
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
