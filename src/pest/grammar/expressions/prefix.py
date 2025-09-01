"""pest positive and negative predicate expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest.grammar.expression import Success
    from pest.state import ParserState


class PositivePredicate(Expression):
    """A pest grammar positive predicate expression.

    This corresponds to the `&` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}&{self.expression}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
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

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}!{self.expression}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
