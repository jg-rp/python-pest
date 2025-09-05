"""Special rules for SOi and EOI."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar.expression import Success
from pest.grammar.expression import Terminal
from pest.grammar.expressions.rule import Rule

if TYPE_CHECKING:
    from pest.state import ParserState


class SOI(Rule):
    """A built-in rule matching the start of input."""

    def __init__(self) -> None:
        super().__init__("SOI", _SOI(), "_", None)


class EOI(Rule):
    """A built-in rule matching the end of input."""

    def __init__(self) -> None:
        super().__init__("EOI", _EOI(), "_", None)


class _SOI(Terminal):
    """A built-in terminal matching the start of input."""

    def __str__(self) -> str:
        return "SOI"

    def parse(self, _state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        if start == 0:
            yield Success(None, 0)


class _EOI(Terminal):
    """A built-in rule matching the end of input."""

    def __str__(self) -> str:
        return "EOI"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        if start == len(state.input):
            yield Success(None, start)
