"""The sequence (`~`) expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar import Expression
from pest.grammar.expression import Success
from pest.node import Node

if TYPE_CHECKING:
    from pest.state import ParserState


class Sequence(Expression):
    """Expression that matches a sequence of sub-expressions in order.

    This corresponds to the `~` operator in pest.
    """

    __slots__ = ("left", "right")

    def __init__(self, left: Expression, right: Expression, tag: str | None = None):
        super().__init__(tag)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.left} ~ {self.right}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse left followed by right starting at `start`.

        Yields:
            - One `Success` if both sides matched.
            - Nothing if either side fails.
        """
        # XXX: This is not right
        for left_result in self.left.parse(state, start):
            position = left_result.pos
            children: list[Node] = []

            if left_result.node:
                children.append(left_result.node)

            for ws_result in state.parse_implicit_rules(position):
                position = ws_result.pos
                if ws_result.node:
                    children.append(ws_result.node)

            for right_result in self.right.parse(state, position):
                position = right_result.pos
                if right_result.node:
                    children.append(right_result.node)

                yield Success(
                    Node(start=start, end=position, children=children, tag=self.tag),
                    position,
                )
