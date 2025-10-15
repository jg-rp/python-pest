"""Special built-in rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar.expression import Expression
from pest.grammar.rule import SILENT
from pest.grammar.rule import BuiltInRule

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.pairs import Pair
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

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: ARG002
        """Attempt to match this expression against the input at `start`."""
        if state.pos < len(state.input):
            state.pos += 1
            return True
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:  # noqa: ARG002
        """Emit Python source code that implements this grammar expression."""
        gen.writeln("if state.pos < len(state.input):")
        with gen.block():
            gen.writeln("state.pos += 1")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")

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

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: ARG002
        """Attempt to match this expression against the input at `start`."""
        return state.pos == 0

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:  # noqa: ARG002
        """Emit Python source code that implements this grammar expression."""
        gen.writeln("if state.pos == 0:")
        with gen.block():
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")

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

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: ARG002
        """Attempt to match this expression against the input at `start`."""
        return state.pos == len(state.input)

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:  # noqa: ARG002
        """Emit Python source code that implements this grammar expression."""
        gen.writeln("if state.pos != len(state.input):")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = True")

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert not expressions
        return self
