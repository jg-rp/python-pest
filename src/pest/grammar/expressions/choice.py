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

    __slots__ = ("left", "right")

    def __init__(self, left: Expression, right: Expression):
        super().__init__(None)
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.left} | {self.right}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.left == other.left
            and self.right == other.right
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.left, self.right, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        success = False

        for left_result in state.parse(self.left, start):
            success = True
            yield left_result

        if not success:
            for right_result in state.parse(self.right, start):
                yield right_result

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.left, self.right]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)
