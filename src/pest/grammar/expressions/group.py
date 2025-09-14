"""A pest grammar expression group."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from typing_extensions import Self

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest.grammar.expression import Success
    from pest.state import ParserState


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

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # XXX: Do we need a `Group` expression?
        # A group might have a tag.
        yield from state.parse(self.expression, start)

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)
