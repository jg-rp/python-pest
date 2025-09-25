"""Special built-in rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar.expression import Expression
from pest.grammar.expression import Match
from pest.grammar.rule import SILENT
from pest.grammar.rule import BuiltInRule

if TYPE_CHECKING:
    from pest.state import ParserState


class Any(BuiltInRule):
    """A built-in rule matching any single "character"."""

    def __init__(self) -> None:
        super().__init__("ANY", _Any(), SILENT, None)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Any)

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 1
        assert isinstance(expressions[0], _Any)
        return self


class _Any(Expression):
    def __str__(self) -> str:
        return "ANY"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        if start < len(state.input):
            return [Match(None, start + 1)]
        return None

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert not expressions
        return self


class SOI(BuiltInRule):
    """A built-in rule matching the start of input."""

    def __init__(self) -> None:
        super().__init__("SOI", _SOI(), SILENT, None)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SOI)

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 1
        assert isinstance(expressions[0], _SOI)
        return self


class _SOI(Expression):
    def __str__(self) -> str:
        return "SOI"

    def parse(self, _state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        if start == 0:
            return [Match(None, 0)]
        return None

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert not expressions
        return self


class EOI(BuiltInRule):
    """A built-in rule matching the end of input."""

    def __init__(self) -> None:
        super().__init__("EOI", _EOI(), 0, None)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EOI)

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 1
        assert isinstance(expressions[0], _EOI)
        return self


class _EOI(Expression):
    def __str__(self) -> str:
        return "EOI"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        if start == len(state.input):
            return [Match(None, start)]
        return None

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert not expressions
        return self
