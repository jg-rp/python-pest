"""The sequence (`~`) expression."""

from pest import Expression
from pest import Node
from pest import ParserState
from pest.expressions import Term


class Sequence(Expression):
    """Expression that matches a sequence of sub-expressions in order.

    This corresponds to the `~` operator in pest.
    """

    def __init__(self, *terms: Term):
        self.terms: tuple[Term, ...] = terms

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        children: list[Node] = []
        position = start

        for term in self.terms:
            result = term.parse(state, position)
            if result is None:
                return None  # fail immediately
            node, position = result
            children.append(node)

        return (Node(start=start, end=position, children=children), position)
