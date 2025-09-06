"""Special built-in rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar.expression import Success
from pest.grammar.expressions.rule import BuiltInRule

if TYPE_CHECKING:
    from pest.state import ParserState


class Any(BuiltInRule):
    """A built-in rule matching any single "character"."""

    def __init__(self) -> None:
        super().__init__("ANY", "_", None)

    def __str__(self) -> str:
        return "ANY"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Any)

    def __hash__(self) -> int:
        return hash(self.__class__)

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if start < len(state.input):
            yield Success(None, start + 1)
