"""The sequence (`~`) expression."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Expression
from pest.node import Node
from pest.result import ParseResult

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

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        children: list[Node] = []
        position = start

        result = self.left.parse(state, position)
        if result and result.node:
            children.append(result.node)
            position = result.pos
        else:
            return None

        # TODO: skip if WHITESPACE and/or COMMENT

        result = self.right.parse(state, position)
        if result and result.node:
            children.append(result.node)
            position = result.pos
        else:
            return None

        return ParseResult(Node(start=start, end=position, children=children), position)
