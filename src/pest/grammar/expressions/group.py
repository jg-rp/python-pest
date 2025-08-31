"""A pest grammar expression group."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest import ParserState
    from pest.result import ParseResult


class Group(Expression):
    """A pest grammar expression group.

    This corresponds to `(EXPRESSION)` in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}({self.expression})"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
