"""The sequence (`~`) expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator
from typing import Self

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest.grammar.expression import Match
    from pest.state import ParserState


class Sequence(Expression):
    """Expression that matches a sequence of sub-expressions in order.

    This corresponds to the `~` operator in pest.
    """

    __slots__ = ("expressions",)

    def __init__(self, *expressions: Expression):
        super().__init__(None)
        self.expressions = list(expressions)

    def __str__(self) -> str:
        sequence = " ~ ".join(str(expr) for expr in self.expressions)
        return f"{self.tag_str()}{sequence}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Sequence) and other.expressions == self.expressions

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Try to parse left followed by right starting at `start`."""
        position = start
        results: list[Match] = []
        state.snapshot()

        for i, expr in enumerate(self.expressions):
            result = list(state.parse(expr, position, self.tag))
            if not result:
                state.restore()
                return

            position = result[-1].pos
            results.extend(result)

            # Only skip trivia between expressions, not after the last one.
            if i < len(self.expressions) - 1:
                implicit_result = list(state.parse_implicit_rules(position))
                if implicit_result:
                    position = implicit_result[-1].pos
                    results.extend(implicit_result)

        state.ok()
        yield from results

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return self.expressions

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)
