"""The choice (`|`) operator."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from typing_extensions import Self

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest.grammar.expression import Success
    from pest.state import ParserState


class Choice(Expression):
    """Expression that matches a one of a choice of sub-expressions.

    This corresponds to the `|` operator in pest.
    """

    __slots__ = ("expressions",)

    def __init__(self, *expressions: Expression):
        super().__init__(None)
        self.expressions = list(expressions)

    def __str__(self) -> str:
        choice = " | ".join(str(expr) for expr in self.expressions)
        return f"{self.tag_str()}{choice}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.expressions == other.expressions
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, tuple(self.expressions), self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        for expr in self.expressions:
            if result := list(state.parse(expr, start)):
                yield from result
                break

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return self.expressions

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)
