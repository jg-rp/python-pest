"""Parser generator state."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Iterator
from typing import Sequence

from typing_extensions import Never

from .exceptions import PestParsingError
from .grammar.expression import Success
from .grammar.expressions.rule import Rule
from .stack import Stack

if TYPE_CHECKING:
    from pest.grammar.expression import Expression

    from .parser import Parser


@dataclass
class Attempt:
    """A parse attempt at a specific position."""

    expr: Expression
    pos: int
    positive: bool  # True for positive, False for negative


class ParserState:
    """Holds parsing state.

    Includes input string, current parsing context, and a stack for stateful
    grammar operations.
    """

    __slots__ = (
        "parser",
        "input",
        "_atomic_depth",
        "stack",
        "cache",
        "rule_stack",
        "attempts",
        "furthest_failure",
        "neg_pred",
    )

    def __init__(self, parser: Parser, input_: str) -> None:
        self.parser = parser
        self.input = input_
        # TODO: a snapshotting int class?
        self._atomic_depth: list[int] = [0]
        self.stack: Stack[str] = Stack()  # User stack
        self.cache: dict[tuple[int, int], list[Success] | None] = {}
        self.rule_stack: list[Rule] = []
        self.attempts: list[Attempt] = []
        self.neg_pred: int = 0  # Negative predicate depth.
        self.furthest_failure: tuple[int, list[Attempt]] | None = None

    @property
    def atomic_depth(self) -> int:
        """The current atomic rule state."""
        return self._atomic_depth[-1]

    @atomic_depth.setter
    def atomic_depth(self, value: int) -> None:
        """Set the current atomic depth."""
        self._atomic_depth[-1] = value

    def parse(self, expr: Expression, pos: int) -> Iterator[Success]:
        """Parse `expr` or return a cached parse result."""
        # XXX: Caching often slows things down, depending on the grammar.
        key = (pos, id(expr)) if expr.is_pure(self.parser.rules) else None
        if key and key in self.cache:
            cached = self.cache[key]
            if cached is not None:
                yield from cached
            return

        # TODO: context manager for rule stack?
        if isinstance(expr, Rule):
            self.rule_stack.append(expr)

        self.attempts.append(Attempt(expr, pos, self.neg_pred == 0))
        results = list(expr.parse(self, pos))

        if isinstance(expr, Rule):
            assert id(self.rule_stack.pop()) == id(expr)

        # Empty `results` indicates a failed parse.
        if results:
            if key:
                self.cache[key] = results
            yield from results
        else:
            if key:
                self.cache[key] = None

            if (
                self.furthest_failure is None
                or pos > self.furthest_failure[0]
                or (pos == self.furthest_failure[0] and self.neg_pred == 0)
            ):
                # Save a copy of the stack at this failure point
                self.furthest_failure = (pos, self.attempts.copy())

        self.attempts.pop()

    def raise_failure(self) -> Never:
        """Return a PestParsingError populated with context info."""
        if not self.furthest_failure:
            raise PestParsingError("no parse attempts recorded", [], [], -1, "", (0, 0))

        pos, attempts = self.furthest_failure

        if not attempts:
            raise PestParsingError(
                f"error at {pos}: unknown failure", [], [], pos, "", (0, 0)
            )

        furthest = max(attempts, key=lambda a: a.pos)
        expr = furthest.expr
        pos = furthest.pos
        positive = furthest.positive

        line = self.input.count("\n", 0, pos) + 1
        col = pos - self.input.rfind("\n", 0, pos)
        found = self.input[pos : pos + 10] or "end of input"

        context = "expected" if positive else "unexpected"

        # TODO: Find nearest rule. We don't want to show the names of internal
        # expression classes.
        rule = (
            getattr(expr, "name", None)
            if hasattr(expr, "name")
            else expr.__class__.__name__
        )

        # TODO: something with stack trace
        stack_trace = " > ".join(
            getattr(a.expr, "name", str(a.expr)) for a in attempts if a.positive
        )

        msg = f"error at {line}:{col} in {rule}: {context} {expr}, found {found!r}"

        # TODO: if furthest is Choice, positive and negative come from Choice.expression

        raise PestParsingError(
            msg,
            [
                str(attempt.expr)
                for attempt in self.furthest_failure[1]
                if attempt.positive
            ],
            [
                str(attempt.expr)
                for attempt in self.furthest_failure[1]
                if not attempt.positive
            ],
            pos,
            "",  # TODO: current line
            (line, col),
        )

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

            # XXX: bit of a hack
            # We're relying on knowing the name of the current rule so we don't
            # recurse indefinitely when parsing COMMENT, which will often
            # include a sequence with implicit whitespace.
            if comment_rule and (
                not self.rule_stack or self.rule_stack[-1].name != "COMMENT"
            ):
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
        self.stack.push(value)

    def drop(self) -> None:
        """Pops one item from the top of the stack."""
        self.stack.pop()

    def peek(self) -> str | None:
        """Peek at the top element of the stack."""
        return self.stack.peek()

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
            return self.stack[:]
        return self.stack[slice(start, end)]

    def snapshot(self) -> None:
        """Mark the current state as a checkpoint."""
        self.stack.snapshot()
        self._atomic_depth.append(self.atomic_depth)

    def ok(self) -> None:
        """Discard the last checkpoint after a successful match."""
        self.stack.drop_snapshot()
        self.atomic_depth = self._atomic_depth.pop()

    def restore(self) -> None:
        """Restore the state to the most recent checkpoint."""
        self.stack.restore()
        self._atomic_depth.pop()

    @contextmanager
    def suppress(self) -> Iterator[ParserState]:
        """A context manager that resets parser state on exit."""
        self.stack.snapshot()
        # TODO: rule stack too?
        atomic_depth = self.atomic_depth
        yield self
        self.atomic_depth = atomic_depth
        self.stack.restore()

    @contextmanager
    def negative_predicate(self) -> Iterator[ParserState]:
        """A context manager that increments and decrements negative predicate depth."""
        self.neg_pred += 1
        try:
            yield self
        finally:
            self.neg_pred -= 1
