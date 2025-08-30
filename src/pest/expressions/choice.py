"""The choice (`|`) expression."""

from pest import Expression
from pest import Node
from pest import ParserState
from pest.expressions import Term


class Choice(Expression):
    """Expression that matches a one of a choice of sub-expressions.

    This corresponds to the `|` operator in pest.
    """

    def __init__(self, *terms: Term):
        self.terms: tuple[Term, ...] = terms

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
