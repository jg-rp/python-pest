"""pest positive and negative predicate expressions."""

from __future__ import annotations

from pest import Expression
from pest import Node
from pest import ParserState
from pest import Token


class PositivePredicate(Expression):
    """A pest grammar positive predicate expression.

    This corresponds to the `&` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: Token | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"&{self.expression}"

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class NegativePredicate(Expression):
    """A pest grammar negative predicate expression.

    This corresponds to the `!` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: Token | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"!{self.expression}"

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
