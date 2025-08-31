"""The choice (`|`) expression."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Expression
from pest.node import Node
from pest.result import ParseResult

if TYPE_CHECKING:
    from pest import ParserState


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

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse left then right in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        result = self.left.parse(state, start)
        if result and result.node:
            return ParseResult(
                Node(start=start, end=result.pos, children=[result.node]), result.pos
            )

        result = self.right.parse(state, start)
        if result and result.node:
            return ParseResult(
                Node(start=start, end=result.pos, children=[result.node]), result.pos
            )

        return None
