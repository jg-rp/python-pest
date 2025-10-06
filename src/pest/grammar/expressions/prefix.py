"""pest positive and negative predicate expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar import Expression
from pest.grammar.expression import Match

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.state import ParserState


class PositivePredicate(Expression):
    """A pest grammar positive predicate expression.

    This corresponds to the `&` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}&{self.expression}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PositivePredicate) and self.expression == other.expression
        )

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Try to parse all parts in sequence starting at `pos`."""
        with state.suppress() as _state:
            pairs = _state.parse(self.expression, start, self.tag)

        if pairs:
            return [Match(None, start)]
        return None

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:  # noqa: ARG002
        """Emit Python code for a positive lookahead (&E)."""
        gen.writeln("# <PositivePredicate>")

        tmp_pairs = gen.new_temp("children")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")

        gen.writeln("state.checkpoint()")
        self.expression.generate(gen, matched_var, tmp_pairs)

        gen.writeln(f"if {matched_var}:")
        with gen.block():
            # Always restore, even on success
            gen.writeln("state.restore()")
            gen.writeln(f"{tmp_pairs}.clear()  # discard lookahead children")
        gen.writeln("else:")
        with gen.block():
            gen.writeln("state.restore()")

        gen.writeln("# </PositivePredicate>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)


class NegativePredicate(Expression):
    """A pest grammar negative predicate expression.

    This corresponds to the `!` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}!{self.expression}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, NegativePredicate) and self.expression == other.expression
        )

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Try to parse all parts in sequence starting at `pos`."""
        with state.suppress(negative=True) as _state:
            pairs = _state.parse(self.expression, start, self.tag)

        if not pairs:
            return [Match(None, start)]

        return None

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:  # noqa: ARG002
        """Emit Python code for a negative lookahead (!E)."""
        gen.writeln("# <NegativePredicate>")

        tmp_pairs = gen.new_temp("children")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")

        gen.writeln("state.checkpoint()")
        gen.writeln("state.neg_pred_depth += 1")
        self.expression.generate(gen, matched_var, tmp_pairs)

        gen.writeln(f"if not {matched_var}:")
        with gen.block():
            # Inner failed, so the negative predicate succeeds.
            gen.writeln("state.restore()")
            gen.writeln(f"{tmp_pairs}.clear()  # discard lookahead children")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            # Inner matched, so the negative predicate fails.
            gen.writeln("state.restore()")
            gen.writeln(f"{matched_var} = False")

        gen.writeln("state.neg_pred_depth -= 1")
        gen.writeln("# </NegativePredicate>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)
