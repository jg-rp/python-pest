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
    """Base class for all rules."""

    __slots__ = ("name", "expression", "modifier", "doc")

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
            state.atomic_depth = restore_atomic_depth
            return

        end = results[-1].pos

        if self.modifier == "_":
            # Yield children without an enclosing Pair
            yield from results
        elif self.modifier == "@":
            # XXX: children could be non-atomic with `!` modifier
            # Atomic rule silences children
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


class GrammarRule(Rule):
    """A named grammar rule."""


class BuiltInRule(Rule):
    """The base class for all built-in rules."""
