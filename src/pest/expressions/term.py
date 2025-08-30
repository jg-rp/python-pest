"""A pest grammar "term"."""

from __future__ import annotations

from pest import Expression
from pest import Node
from pest import ParserState
from pest import Token


class Term(Expression):
    """A pest grammar "term".

    Includes an optional tag, any prefix operators, an expression and any
    postfix operators.
    """

    __slots__ = ("expression", "tag", "prefix_op", "postfix_op")

    def __init__(
        self,
        expression: Expression,
        tag: Token | None = None,
        prefix_op: Token | None = None,
        postfix_op: list[Token] | None = None,
    ):
        self.expression = expression
        self.tag = tag
        self.prefix_op = prefix_op
        # TODO: preprocess postfix op
        self.postfix_op = postfix_op

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
