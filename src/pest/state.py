"""Parser interpreter state."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from .grammar.rule import Rule
from .stack import PersistentStack
from .stack import Stack

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Iterator
    from collections.abc import Sequence

    from .pairs import Pair
    from .parser import Parser


class ParserState:
    """Encapsulates the mutable state of a parser.

    The `ParserState` tracks the input text, current position, and multiple stacks
    for user values and modifiers. It supports checkpointing, restoration, and
    stack operations to facilitate backtracking.

    Args:
        text: The input string to be parsed.
        start_pos: The index in `text` to start parsing from.
    """

    __slots__ = (
        "_pos_checkpoints",
        "_suppress_failures",
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
        "_atomic_depth_checkpoints",
    )

    def __init__(
        self, text: str, start_pos: int = 0, parser: Parser | None = None
    ) -> None:
        self.input = text
        self.parser = parser  # Always None in generated code.

        # Negative predicate depth
        self.neg_pred_depth = 0

        # Failure tracking
        self.furthest_pos = -1
        self.furthest_expected: dict[str, list[str]] = {}
        self.furthest_unexpected: dict[str, list[str]] = {}
        self.furthest_stack: Iterable[Rule | RuleFrame] = []
        self._suppress_failures = False

        # Ths current index into `self.input` with checkpoints for backtracking.
        self.pos = start_pos
        self._pos_checkpoints: list[int] = []

        # The number of atomic rules in the rule stack with checkpoints for
        # backtracking.
        self.atomic_depth = 0
        self._atomic_depth_checkpoints: list[int] = []

        self.rule_stack = PersistentStack[Rule | RuleFrame]()
        self.tag_stack: list[str] = []  # User tags are always enabled
        self.user_stack = Stack[str]()  # PUSH/POP/PEEK/DROP

    def parse_trivia(self, pairs: list[Pair]) -> bool:
        """Parse any implicit rules (`WHITESPACE` and `COMMENT`)."""
        if self.atomic_depth > 0:
            return False

        assert self.parser

        if skip := self.parser.rules.get("SKIP"):
            return skip.parse(self, pairs)

        # Unoptimized whitespace and comment rules.
        whitespace_rule = self.parser.rules.get("WHITESPACE")
        comment_rule = self.parser.rules.get("COMMENT")

        if not whitespace_rule and not comment_rule:
            return False

        children: list[Pair] = []
        some = False

        with self.suppress_failures():
            while True:
                matched = False

                if whitespace_rule:
                    matched = whitespace_rule.parse(self, children)
                    if matched:
                        some = True
                        pairs.extend(children)
                        # continue
                    children.clear()

                if comment_rule:
                    self.checkpoint()
                    matched = comment_rule.parse(self, children) or matched
                    if matched:
                        some = True
                        pairs.extend(children)
                        self.ok()
                    else:
                        self.restore()
                    children.clear()

                if not matched:
                    break

        return some

    def checkpoint(self) -> None:
        """Take a snapshot of the current state for potential backtracking.

        Saves the current state of all stacks, allowing restoration if parsing fails.
        """
        self.user_stack.snapshot()
        self.rule_stack.snapshot()
        self._atomic_depth_checkpoints.append(self.atomic_depth)
        self._pos_checkpoints.append(self.pos)

    def ok(self) -> None:
        """Commit to the current state after a successful parse.

        Discards the last checkpoint, making the changes since the last checkpoint
        permanent.
        """
        self.user_stack.drop_snapshot()
        self.rule_stack.ok()
        self._atomic_depth_checkpoints.pop()
        self._pos_checkpoints.pop()

    def restore(self) -> None:
        """Restore the state to the most recent checkpoint.

        Reverts all stacks to their state at the last checkpoint, undoing any changes
        since then.
        """
        self.user_stack.restore()
        self.rule_stack.restore()
        self.atomic_depth = self._atomic_depth_checkpoints.pop()
        self.pos = self._pos_checkpoints.pop()

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
        self._atomic_depth_checkpoints.append(self.atomic_depth)
        yield self
        self.atomic_depth = self._atomic_depth_checkpoints.pop()

    @contextmanager
    def suppress_failures(self) -> Iterator[ParserState]:
        """A context manager that prevents rules contributing to failures."""
        self._suppress_failures = True
        yield self
        self._suppress_failures = False

    @contextmanager
    def tag(self, tag_: str) -> Iterator[ParserState]:
        """A context manager that removes `tag_` on exit."""
        self.tag_stack.append(tag_)
        yield self
        if self.tag_stack:
            self.tag_stack.pop()

    def fail(
        self,
        label: str,
        *,
        pos: int | None = None,
        rule_name: str | None = None,
        force: bool = False,
    ) -> None:
        """Record a failure, inferring expected vs. unexpected context."""
        if (self.neg_pred_depth > 0 and not force) or self._suppress_failures:
            return

        is_neg_context = self.neg_pred_depth % 2 == 1
        rule_name = rule_name or self.rule_stack.peek().name
        pos = pos or self.pos

        if pos > self.furthest_pos:
            self.furthest_pos = pos
            self.furthest_stack = self.rule_stack.copy()
            if is_neg_context:
                self.furthest_unexpected = {rule_name: [label]}
                self.furthest_expected = {}
            else:
                self.furthest_expected = {rule_name: [label]}
                self.furthest_unexpected = {}
        elif pos == self.furthest_pos:
            target = (
                self.furthest_unexpected if is_neg_context else self.furthest_expected
            )

            if rule_name in target:
                target[rule_name].append(label)
            else:
                target[rule_name] = [label]


class RuleFrame:
    """Rule meta data for the generated rule stack.

    Generated parser don't have access to complete `Rule` object. `RuleFrame`
    is a lightweight stand in.

    Attributes:
        name (str): The rule's name.
        modifier (int): A bit mask encoding modifiers applied to the rule.
    """

    __slots__ = ("name", "modifier")

    def __init__(self, name: str, modifier: int):
        self.name = name
        self.modifier = modifier

    def __repr__(self) -> str:
        return f"RuleFrame({self.name!r}, {self.modifier})"

    def __hash__(self) -> int:
        return hash((self.name, self.__class__.__name__))
