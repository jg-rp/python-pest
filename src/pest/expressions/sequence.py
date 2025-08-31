"""The sequence (`~`) expression."""

from pest import Expression
from pest import Node
from pest import ParserState
from pest import Token


class Sequence(Expression):
    """Expression that matches a sequence of sub-expressions in order.

    This corresponds to the `~` operator in pest.
    """

    __slots__ = ("left", "right")

    def __init__(self, left: Expression, right: Expression, tag: Token | None = None):
        super().__init__(tag)
        self.left = left
        self.right = right

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        children: list[Node] = []
        position = start

        if result := self.left.parse(state, position):
            children.append(result[0])
            position = result[1]
        else:
            return None

        if result := self.right.parse(state, position):
            children.append(result[0])
            position = result[1]
        else:
            return None

        return (Node(start=start, end=position, children=children), position)
