"""Special rules for SOi and EOI."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar.expression import Success
from pest.grammar.expressions.rule import BuiltInRule

if TYPE_CHECKING:
    from pest.state import ParserState


class SOI(BuiltInRule):
    """A built-in rule matching the start of input."""

    def __init__(self) -> None:
        super().__init__("SOI", "_", None)

    def __str__(self) -> str:
        return "SOI"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SOI)

    def __hash__(self) -> int:
        return hash(self.__class__)

    def parse(self, _state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if start == 0:
            yield Success(None, 0)


class EOI(BuiltInRule):
    """A built-in rule matching the end of input."""

    def __init__(self) -> None:
        super().__init__("EOI", "_", None)

    def __str__(self) -> str:
        return "EOI"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SOI)

    def __hash__(self) -> int:
        return hash(self.__class__)

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if start == len(state.input):
            yield Success(None, start)
