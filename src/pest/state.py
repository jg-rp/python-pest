"""Parser interpreter state."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from .checkpoint_int import SnapshottingInt
from .grammar.rule import Rule
from .stack import Stack

if TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Sequence

    from .pairs import Pair
    from .parser import Parser


# TODO: can we use the same state implementation for both interpreted and
# generates parsers? The only difference is `parse_trivia()` and `Rule`
# instead of `RuleFrame`.


class ParserState:
    """Holds parsing state.

    Includes input string, current parsing context, and a stack for stateful
    grammar operations.
    """

    __slots__ = (
        "_pos_history",
        "atomic_depth",
        "furthest_expected",
        "furthest_pos",
        "furthest_stack",
        "furthest_unexpected",
        "input",
        "neg_pred_depth",
        "parser",
        "pos",
        "rule_stack",
        "tag_stack",
        "user_stack",
    )

    def __init__(self, parser: Parser, input_: str, start_pos: int = 0) -> None:
        self.parser = parser
        self.input = input_
        self.pos = start_pos

        # Negative predicate depth
        self.neg_pred_depth = 0

        # Failure tracking
        self.furthest_pos = -1
        self.furthest_expected: dict[str, int] = {}
        self.furthest_unexpected: dict[str, int] = {}
        self.furthest_stack: list[Rule] = []

        self.user_stack = Stack[str]()  # PUSH/POP/PEEK/DROP
        self.rule_stack = Stack[Rule]()
        self._pos_history: list[int] = []  # TODO: better
        self.atomic_depth = SnapshottingInt()
        self.tag_stack: list[str] = []

    def parse_trivia(self, pairs: list[Pair]) -> bool:
        """Parse any implicit rules (`WHITESPACE` and `COMMENT`) starting at `pos`.

        Returns a list of ParseResult instances. Each result represents one
        successful application of an implicit rule. `node` will be None if
        the rule was silent.
        """
        if self.atomic_depth > 0:
            return False

        # TODO: look for optimized SKIP rule

        # Unoptimized whitespace and comment rules.
        whitespace_rule = self.parser.rules.get("WHITESPACE")
        comment_rule = self.parser.rules.get("COMMENT")

        if not whitespace_rule and not comment_rule:
            return False

        children: list[Pair] = []
        some = False

        while True:
            matched = False

            if whitespace_rule:
                matched = whitespace_rule.parse(self, children)
                if matched:
                    some = True
                    pairs.extend(children)

            if comment_rule and (
                not self.rule_stack or self.rule_stack[-1].name != "COMMENT"
            ):
                self.checkpoint()
                matched = comment_rule.parse(self, children) or matched
                if matched:
                    some = True
                    pairs.extend(children)
                    self.ok()
                else:
                    self.restore()

            if not matched:
                break

        return some

    def checkpoint(self) -> None:
        """Take a snapshot of the current state for potential backtracking.

        Saves the current state of all stacks, allowing restoration if parsing fails.
        """
        self.user_stack.snapshot()
        self.rule_stack.snapshot()
        self.atomic_depth.snapshot()
        self._pos_history.append(self.pos)

    def ok(self) -> None:
        """Commit to the current state after a successful parse.

        Discards the last checkpoint, making the changes since the last checkpoint
        permanent.
        """
        self.user_stack.drop_snapshot()
        self.rule_stack.drop_snapshot()
        self.atomic_depth.drop()
        self._pos_history.pop()

    def restore(self) -> None:
        """Restore the state to the most recent checkpoint.

        Reverts all stacks to their state at the last checkpoint, undoing any changes
        since then.
        """
        self.user_stack.restore()
        self.rule_stack.restore()
        self.atomic_depth.restore()
        self.pos = self._pos_history.pop()

    def push(self, value: str) -> None:
        """Push a value onto the user stack.

        Args:
            value: The value to push onto the stack.
        """
        self.user_stack.push(value)

    def drop(self) -> None:
        """Pop one item from the top of the user stack."""
        self.user_stack.pop()

    def peek(self) -> str | None:
        """Return the value at the top of the user stack, or None if empty."""
        return self.user_stack.peek()

    def peek_slice(
        self, start: int | None = None, end: int | None = None
    ) -> Sequence[str]:
        """Peek at a slice of the user stack, similar to pest's `PEEK(start..end)`.

        Args:
            start: Start index of the slice (0 = bottom of stack).
            end:   End index of the slice (exclusive).

        Returns:
            A list of values from the stack slice. If no arguments are given,
            returns the entire stack.

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

    @contextmanager
    def atomic_checkpoint(self) -> Iterator[ParserState]:
        """A context manager that restores atomic depth on exit."""
        self.atomic_depth.snapshot()
        try:
            yield self
        finally:
            self.atomic_depth.restore()

    @contextmanager
    def tag(self, tag_: str) -> Iterator[ParserState]:
        """A context manager that removes `tag_` on exit."""
        self.tag_stack.append(tag_)
        try:
            yield self
        finally:
            if self.tag_stack:
                self.tag_stack.pop()

    def fail(self, label: str) -> None:
        """Record a failure, inferring expected vs. unexpected context."""
        is_neg_context = self.neg_pred_depth % 2 == 1

        if self.pos > self.furthest_pos:
            self.furthest_pos = self.pos
            self.furthest_stack = list(self.rule_stack)
            if is_neg_context:
                self.furthest_unexpected = {label: 1}
                self.furthest_expected = {}
            else:
                self.furthest_expected = {label: 1}
                self.furthest_unexpected = {}
        elif self.pos == self.furthest_pos:
            target = (
                self.furthest_unexpected if is_neg_context else self.furthest_expected
            )

            target[label] = 1
