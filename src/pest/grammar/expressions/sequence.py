"""The sequence (`~`) expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest.grammar.expression import Success
    from pest.state import ParserState


class Sequence(Expression):
    """Expression that matches a sequence of sub-expressions in order.

    This corresponds to the `~` operator in pest.
    """

    __slots__ = ("left", "right")

    def __init__(self, left: Expression, right: Expression):
        super().__init__(None)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.left} ~ {self.right}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse left followed by right starting at `start`."""
        left_results = list(self.left.parse(state, start))
        if not left_results:
            return  # left failed

        position = left_results[-1].pos
        implicit_results = list(state.parse_implicit_rules(position))
        if implicit_results:
            position = implicit_results[-1].pos

        right_results = list(self.right.parse(state, position))
        if not right_results:
            return  # right failed

        # If both sides matched, yield everything in sequence.
        yield from self.filter_silent(left_results)
        yield from self.filter_silent(implicit_results)
        yield from self.filter_silent(right_results)
