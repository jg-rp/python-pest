"""A logical grammar rule."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterable
from typing import Iterator

from typing_extensions import Self

from pest.grammar import Expression
from pest.grammar.expression import Success
from pest.pairs import Pair

if TYPE_CHECKING:
    from pest.state import ParserState


class Rule(Expression):
    """A named grammar rule."""

    __slots__ = ("name", "modifier", "expression", "doc")

    def __init__(
        self,
        name: str,
        expression: Expression,
        modifier: str | None = None,
        doc: Iterable[str] | None = None,
    ):
        super().__init__(tag=None)
        self.name = name
        self.expression = expression
        self.modifier = modifier
        self.doc = tuple(doc) if doc else None

    def __str__(self) -> str:
        doc = "".join(f"///{line}\n" for line in self.doc) if self.doc else ""
        modifier = self.modifier if self.modifier else ""
        return f"{doc}{self.name} = {modifier}{{ {self.expression} }}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.expression == other.expression
            and self.modifier == other.modifier
            and self.doc == other.doc
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash(
            (self.__class__, self.expression, self.modifier, self.doc, self.tag)
        )

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state.
            start: The index in the input string where parsing begins.
        """
        restore_atomic_depth = state.atomic_depth

        if self.modifier in ("@", "$"):
            state.atomic_depth += 1
        elif self.modifier == "!":
            state.atomic_depth = 0

        results = list(state.parse(self.expression, start))
        if not results:
            return

        end = results[-1].pos

        if self.modifier == "_":
            # Silent rule succeeds, but no node is returned.
            yield Success(None, end)
        elif self.modifier == "$":
            # Compound-atomic rule discards children
            yield Success(
                Pair(
                    input_=state.input,
                    rule=self,
                    start=start,
                    end=end,
                    children=[],
                ),
                pos=end,
            )
        else:
            yield Success(
                Pair(
                    input_=state.input,
                    rule=self,
                    start=start,
                    end=end,
                    children=[success.pair for success in results if success.pair],
                ),
                pos=end,
            )

        # Restore atomic depth to what it was before this rule
        state.atomic_depth = restore_atomic_depth

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(self.name, expressions[0], self.modifier, self.doc)
