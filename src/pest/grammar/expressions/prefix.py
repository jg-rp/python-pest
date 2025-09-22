"""pest positive and negative predicate expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from typing_extensions import Self

from pest.grammar import Expression
from pest.grammar.expression import Success

if TYPE_CHECKING:
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

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PositivePredicate) and self.expression == other.expression
        )

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        with state.suppress() as _state:
            pairs = list(_state.parse(self.expression, start, self.tag))

        if pairs:
            yield Success(None, start)

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)


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

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, NegativePredicate) and self.expression == other.expression
        )

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        with state.suppress(negative=True) as _state:
            pairs = list(_state.parse(self.expression, start, self.tag))

        if not pairs:
            yield Success(None, start)

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)
