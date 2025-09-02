"""A logical grammar rule."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

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
        doc: list[str] | None = None,
    ):
        super().__init__(tag=None)
        self.name = name
        self.expression = expression
        self.modifier = modifier
        self.doc = doc

    def __str__(self) -> str:
        doc = "".join(f"///{line}\n" for line in self.doc) if self.doc else ""
        modifier = self.modifier if self.modifier else ""
        return f"{doc}{self.name} = {modifier}{{ {self.expression} }}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        restore_atomic_depth = state.atomic_depth

        if self.modifier in ("@", "$"):
            state.atomic_depth += 1
        elif self.modifier == "!":
            state.atomic_depth = 0

        results = list(self.expression.parse(state, start))
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
                    rule=self,
                    start=start,
                    end=end,
                    children=[success.pair for success in results if success.pair],
                ),
                pos=end,
            )

        # Restore atomic depth to what it was before this rule
        state.atomic_depth = restore_atomic_depth
