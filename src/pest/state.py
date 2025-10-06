"""Parser interpreter state."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING
from typing import Never

from .checkpoint_int import SnapshottingInt
from .exceptions import PestParsingError
from .grammar.expression import Match
from .grammar.rule import Rule
from .stack import Stack

if TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Sequence

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
        "user_stack",
        "attempts",
        "furthest_failure",
        "neg_pred_depth",
        "tag_stack",
    )

    def __init__(
        self, parser: Parser, input_: str, start_rule: Rule, start_pos: int = 0
    ) -> None:
        self.parser = parser
        self.input = input_

        self.atomic_depth = SnapshottingInt()
        self.neg_pred_depth = SnapshottingInt()  # XXX: we're not currently using this
        self.tag_stack: list[str | None] = []

        self.user_stack: Stack[str] = Stack()

        self.attempts: list[tuple[int, Rule]] = [(start_pos, start_rule)]
        self.furthest_failure: tuple[int, Rule] | None = None

    def parse(
        self, expr: Expression, pos: int, tag: str | None = None
    ) -> list[Match] | None:
        """Parse an expression in the current state."""
        if tag:
            self.tag_stack.append(tag)

        if not isinstance(expr, Rule):
            matches = expr.parse(self, pos)
            if tag and self.tag_stack:
                self.tag_stack.pop()
            return matches

        self.attempts.append((pos, expr))
        matches = expr.parse(self, pos)

        if not matches and (
            self.furthest_failure is None or pos < self.furthest_failure[0]
        ):
            self.furthest_failure = (pos, expr)

        elif matches and self.tag_stack:
            # Tag results with last tag on the tag stack.
            rule_tag = self.tag_stack.pop()
            for match in matches:
                if match.pair:
                    match.pair.tag = rule_tag

        self.attempts.pop()
        if tag and self.tag_stack:
            self.tag_stack.pop()

        return matches

    def raise_failure(self) -> Never:
        """Return a PestParsingError populated with context info."""
        if not self.furthest_failure:
            raise PestParsingError("no parse attempts recorded", [], [], -1, "", (0, 0))

        pos, expr = self.furthest_failure

        # if not attempts:
        #     raise PestParsingError(
        #         f"error at {pos}: unknown failure", [], [], pos, "", (0, 0)
        #     )

        # positive = furthest.positive

        line = self.input.count("\n", 0, pos) + 1
        col = pos - self.input.rfind("\n", 0, pos)
        found = self.input[pos : pos + 10] or "end of input"

        context = "expected"  # if positive else "unexpected"

        msg = (
            f"error at {line}:{col} in {expr.name}: "
            f"{context} {expr.expression}, found {found!r}"
        )

        # TODO: current line
        raise PestParsingError(msg, [], [], pos, "", (line, col))

    def parse_implicit_rules(self, pos: int) -> Iterator[Match]:
        """Parse any implicit rules (`WHITESPACE` and `COMMENT`) starting at `pos`.

        Returns a list of ParseResult instances. Each result represents one
        successful application of an implicit rule. `node` will be None if
        the rule was silent.
        """
        if self.atomic_depth > 0:
            return

        # Unoptimized whitespace and comment rules.
        whitespace_rule = self.parser.rules.get("WHITESPACE")
        comment_rule = self.parser.rules.get("COMMENT")

        if not whitespace_rule and not comment_rule:
            return

        while True:
            new_pos = pos
            matched = False

            if whitespace_rule:
                for result in self.parse(whitespace_rule, new_pos) or []:
                    matched = True
                    new_pos = result.pos
                    if result.pair and self.atomic_depth == 0:
                        yield result

            if comment_rule and (
                not self.attempts or self.attempts[-1][1].name != "COMMENT"
            ):
                for result in self.parse(comment_rule, new_pos) or []:
                    matched = True
                    new_pos = result.pos
                    if result.pair and self.atomic_depth == 0:
                        yield result

            if not matched:
                yield Match(None, new_pos)
                break

            pos = new_pos

    def push(self, value: str) -> None:
        """Push a value onto the stack."""
        self.user_stack.push(value)

    def drop(self) -> None:
        """Pops one item from the top of the stack."""
        self.user_stack.pop()

    def peek(self) -> str | None:
        """Peek at the top element of the stack."""
        return self.user_stack.peek()

    def peek_slice(
        self, start: int | None = None, end: int | None = None
    ) -> Sequence[str]:
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
            return self.user_stack[:]
        return self.user_stack[slice(start, end)]

    def snapshot(self) -> None:
        """Mark the current state as a checkpoint."""
        self.user_stack.snapshot()
        self.atomic_depth.snapshot()
        self.neg_pred_depth.snapshot()

    def ok(self) -> None:
        """Discard the last checkpoint after a successful match."""
        self.user_stack.drop_snapshot()
        self.atomic_depth.drop()
        self.neg_pred_depth.drop()

    def restore(self) -> None:
        """Restore the state to the most recent checkpoint."""
        self.user_stack.restore()
        self.atomic_depth.restore()
        self.neg_pred_depth.restore()

    @contextmanager
    def suppress(self, *, negative: bool = False) -> Iterator[ParserState]:
        """A context manager that resets parser state on exit."""
        self.user_stack.snapshot()
        # TODO: rule stack too?
        self.atomic_depth.snapshot()
        if negative:
            self.neg_pred_depth += 1

        yield self

        if negative:
            self.neg_pred_depth -= 1
        self.atomic_depth.restore()
        self.user_stack.restore()
