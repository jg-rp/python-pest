"""A logical grammar rule."""

from pest.expression import Expression
from pest.node import Node
from pest.state import ParserState
from pest.tokens import Token


class Rule(Expression):
    """A logical grammar rule."""

    __slots__ = ("identifier", "modifier", "expression", "doc")

    def __init__(
        self,
        identifier: Token,
        expression: Expression,
        modifier: Token | None = None,
        doc: list[Token] | None = None,
    ):
        self.identifier = identifier
        self.expression = expression
        self.modifier = modifier
        self.doc = doc

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.

        Returns:
            If parsing succeeds, a `Node` representing the result of the
            matched expression and any child expressions. Or `None` if the
            expression fails to match at `pos`.
        """
        # TODO:
