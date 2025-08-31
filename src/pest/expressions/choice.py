"""The choice (`|`) expression."""

from pest import Expression
from pest import Node
from pest import ParserState
from pest import Token


class Choice(Expression):
    """Expression that matches a one of a choice of sub-expressions.

    This corresponds to the `|` operator in pest.
    """

    __slots__ = ("left", "right")

    def __init__(self, left: Expression, right: Expression, tag: Token | None = None):
        super().__init__(tag)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        # TODO: tag
        return f"{self.left} | {self.right}"

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse left then right in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        if result := self.left.parse(state, start):
            return (Node(start=start, end=result[1], children=[result[0]]), result[1])

        if result := self.right.parse(state, start):
            return (Node(start=start, end=result[1], children=[result[0]]), result[1])

        return None
