"""The choice (`|`) expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest import ParserState
    from pest.grammar.expression import Success


class Choice(Expression):
    """Expression that matches a one of a choice of sub-expressions.

    This corresponds to the `|` operator in pest.
    """

    __slots__ = ("left", "right")

    def __init__(self, left: Expression, right: Expression, tag: str | None = None):
        super().__init__(tag)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.left} | {self.right}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        success = False
        for left_result in self.left.parse(state, start):
            yield left_result
            success = True

        # XXX: ?
        if success:
            return

        yield from self.right.parse(state, start)
