"""The sequence (`~`) expression."""

from pest.expression import Expression
from pest.node import Node
from pest.state import ParserState


class Sequence(Expression):
    """Expression that matches a sequence of sub-expressions in order.

    This corresponds to the `~` operator in pest.
    """

    # TODO: change Expression to Term
    # TODO: Term combines a node with its prefix, postfix and tag.

    def __init__(self, *terms: Expression):
        self.terms: list[Expression] = list(terms)

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
