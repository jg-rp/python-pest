"""The sequence (`~`) expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.grammar.expression import Match
    from pest.state import ParserState


class Sequence(Expression):
    """Expression that matches a sequence of sub-expressions in order.

    This corresponds to the `~` operator in pest.
    """

    __slots__ = ("expressions",)

    def __init__(self, *expressions: Expression):
        super().__init__(None)
        self.expressions = list(expressions)

    def __str__(self) -> str:
        sequence = " ~ ".join(str(expr) for expr in self.expressions)
        return f"{self.tag_str()}{sequence}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Sequence) and other.expressions == self.expressions

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Try to parse left followed by right starting at `start`."""
        position = start
        results: list[Match] = []
        state.snapshot()

        for i, expr in enumerate(self.expressions):
            result = state.parse(expr, position, self.tag)
            if not result:
                state.restore()
                return None

            position = result[-1].pos
            results.extend(result)

            # XXX: If the last expression can't fail, do we still parse implicit rules
            # before it if it does not match anything?

            # Only skip trivia between expressions, not after the last one.
            if i < len(self.expressions) - 1:
                implicit_result = list(state.parse_implicit_rules(position))
                if implicit_result:
                    position = implicit_result[-1].pos
                    results.extend(implicit_result)

        state.ok()
        return results

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a sequence expression (A ~ B ~ ...).

        Each sub-expression is attempted in order. If any one fails, the entire
        sequence fails immediately. Implicit trivia is parsed between items.
        """
        gen.writeln("# <Sequence>")

        inner_matched = gen.new_temp("matched")
        all_ok = gen.new_temp("all_ok")
        gen.writeln(f"{all_ok} = True")

        # Enumerate sub-expressions in order
        for i, child in enumerate(self.expressions):
            # Only continue if all previous succeeded
            gen.writeln(f"if {all_ok}:")
            with gen.block():
                gen.writeln(f"{inner_matched} = False")
                child.generate(gen, inner_matched, pairs_var)
                gen.writeln(f"if not {inner_matched}:")
                with gen.block():
                    gen.writeln(f"{all_ok} = False")

                # Insert trivia except after last expression
                if i < len(self.expressions) - 1:
                    gen.writeln(f"if {all_ok}:")
                    with gen.block():
                        gen.writeln(f"parse_trivia(state, {pairs_var})")

        # Sequence succeeds only if all parts matched
        gen.writeln(f"{matched_var} = {all_ok}")
        gen.writeln("# </Sequence>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return self.expressions

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)
