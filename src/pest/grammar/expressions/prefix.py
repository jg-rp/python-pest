"""pest positive and negative predicate expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar import Expression
from pest.grammar.expressions.terminals import Identifier
from pest.grammar.rule import Rule

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.pairs import Pair
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

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: ARG002
        """Try to parse all parts in sequence starting at `pos`."""
        state.checkpoint()
        matched = self.expression.parse(state, [])
        state.restore()
        return matched

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

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: ARG002
        """Try to parse all parts in sequence starting at `pos`."""
        state.checkpoint()
        state.neg_pred_depth += 1
        matched = self.expression.parse(state, [])
        state.restore()

        if matched:
            # If self.expression is a rule, by now it has been popped off the stack.
            if isinstance(self.expression, Identifier):
                failed_rule_name = self.expression.value
                assert state.parser
                label = str(state.parser.rules[failed_rule_name].expression)
            elif isinstance(self.expression, Rule):
                failed_rule_name = self.expression.name
                label = str(self.expression.expression)
            else:
                failed_rule_name = None
                label = str(self.expression)
            state.fail(label, rule_name=failed_rule_name, force=True)

        state.neg_pred_depth -= 1
        return not matched

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
            # If self.expression is a rule, by now it has been popped off the stack.
            if isinstance(self.expression, Identifier):
                failed_rule_name = self.expression.value
            elif isinstance(self.expression, Rule):
                failed_rule_name = self.expression.name
            else:
                failed_rule_name = ""
            gen.writeln(
                f"state.fail({str(self.expression)!r}, "
                f"rule_name={failed_rule_name!r}, force=True)"
            )

        gen.writeln("state.neg_pred_depth -= 1")
        gen.writeln("# </NegativePredicate>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)
