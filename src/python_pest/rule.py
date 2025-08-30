from .expression import Expression
from .tokens import Token


class Rule:
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
