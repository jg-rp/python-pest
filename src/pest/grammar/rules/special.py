"""Special built-in rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar.expression import Expression
from pest.grammar.expression import Success

if TYPE_CHECKING:
    from pest.state import ParserState


class Any(Expression):
    """A built-in rule matching any single "character"."""

    def __str__(self) -> str:
        return "ANY"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        if start < len(state.input):
            yield Success(None, start + 1)
