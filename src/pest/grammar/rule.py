"""A logical grammar rule."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar import Expression
from pest.grammar.expression import Match
from pest.grammar.expressions.terminals import Identifier
from pest.pairs import Pair

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pest.grammar.codegen.builder import Builder
    from pest.state import ParserState

SILENT = 1 << 1  # _
ATOMIC = 1 << 2  # @
COMPOUND = 1 << 3  # $
NONATOMIC = 1 << 4  # !

SILENT_ATOMIC = SILENT | ATOMIC
SILENT_COMPOUND = SILENT | COMPOUND
SILENT_NONATOMIC = SILENT | NONATOMIC

MODIFIER_SYMBOLS = {
    SILENT: "_",
    ATOMIC: "@",
    COMPOUND: "$",
    NONATOMIC: "!",
}

MODIFIER_MAP = {v: k for k, v in MODIFIER_SYMBOLS.items()}


def modifier_to_str(flags: int) -> str:
    """Convert a modifier bit field into a string of symbols, in defined order."""
    return "".join(symbol for bit, symbol in MODIFIER_SYMBOLS.items() if flags & bit)


class Rule(Expression):
    """Base class for all rules."""

    __slots__ = ("name", "expression", "modifier", "doc", "child_is_non_atomic")

    def __init__(
        self,
        name: str,
        expression: Expression,
        modifier: int,
        doc: Iterable[str] | None = None,
    ):
        super().__init__(tag=None)
        self.name = name
        self.expression = expression
        self.modifier = modifier
        self.doc = tuple(doc) if doc else None

    def __str__(self) -> str:
        doc = "".join(f"///{line}\n" for line in self.doc) if self.doc else ""
        modifier = modifier_to_str(self.modifier)
        return f"{doc}{self.name} = {modifier}{{ {self.expression} }}"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        state.atomic_depth.snapshot()

        if self.modifier & (ATOMIC | COMPOUND):
            state.atomic_depth += 1
        elif self.modifier & NONATOMIC:
            state.atomic_depth.zero()

        results = state.parse(self.expression, start, self.tag)

        # Restore atomic depth to what it was before this rule
        state.atomic_depth.restore()

        if not results:
            return None

        end = results[-1].pos

        if self.modifier & SILENT:
            # Yield children without an enclosing Pair
            return results

        if self.modifier & ATOMIC:
            if isinstance(self.expression, Rule):
                rule: Rule | None = self.expression
            elif isinstance(self.expression, Identifier):
                rule = state.parser.rules.get(self.expression.value)
            else:
                rule = None

            if not rule or not rule.modifier & (NONATOMIC | COMPOUND):
                # Atomic rule silences children
                return [
                    Match(
                        Pair(
                            input_=state.input,
                            rule=self,
                            start=start,
                            end=end,
                            children=[],
                        ),
                        pos=end,
                    )
                ]

            # Non-atomic child rule.
            # XXX: What about children's children?
            return [
                Match(
                    Pair(
                        input_=state.input,
                        rule=self,
                        start=start,
                        end=end,
                        children=[success.pair for success in results if success.pair],
                    ),
                    pos=end,
                )
            ]

        return [
            Match(
                Pair(
                    input_=state.input,
                    rule=self,
                    start=start,
                    end=end,
                    children=[success.pair for success in results if success.pair],
                ),
                pos=end,
            )
        ]

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python source code that implements this grammar expression."""
        gen.writeln("def inner(state: State, pairs: list[Pair]) -> bool:")
        with gen.block():
            gen.writeln(f'"""Parse {self.name}."""')

            start_pos = gen.new_temp("pos")
            if not self.modifier & SILENT:
                gen.writeln(f"{start_pos} = state.pos")

            # `rule_frame` is defined in the closure by `generate_rule`.
            gen.writeln("state.rule_stack.push(rule_frame)")

            inner_pairs = gen.new_temp("children")
            gen.writeln(f"{inner_pairs}: list[Pair] = []")

            if self.modifier & (ATOMIC | COMPOUND):
                gen.writeln("with state.atomic_checkpoint():")
                with gen.block():
                    gen.writeln("state.atomic_depth += 1")
                    self.expression.generate(gen, matched_var, inner_pairs)
            elif self.modifier & NONATOMIC:
                gen.writeln("with state.atomic_checkpoint():")
                with gen.block():
                    gen.writeln("state.atomic_depth.zero()")
                    self.expression.generate(gen, matched_var, inner_pairs)
            else:
                self.expression.generate(gen, matched_var, inner_pairs)

            gen.writeln("state.rule_stack.pop()")

            children: str = inner_pairs

            if self.modifier & SILENT:
                gen.writeln(f"# Silent rule {self.name!r}")
                gen.writeln(f"{pairs_var}.extend({children})")
                gen.writeln(f"return {matched_var}")
            else:
                # Tag child pairs with the last tag on the stack
                tag_var = gen.new_temp("tag")
                gen.writeln("if state.tag_stack:")
                with gen.block():
                    gen.writeln(f"{tag_var}: str | None = state.tag_stack.pop()")
                gen.writeln("else:")
                with gen.block():
                    gen.writeln(f"{tag_var} = None")

                if self.modifier & ATOMIC:
                    gen.writeln(f"# Atomic rule: {self.name!r}")
                    assert gen.rules is not None
                    if isinstance(self.expression, Rule):
                        rule: Rule | None = self.expression
                    elif isinstance(self.expression, Identifier):
                        rule = gen.rules.get(self.expression.value)
                    else:
                        rule = None

                    if not rule or not rule.modifier & (NONATOMIC | COMPOUND):
                        children = "[]"

                pair = (
                    f"Pair("
                    f"state.input, {start_pos}, state.pos, "
                    f"rule_frame, {children}, {tag_var},"
                    ")"
                )

                gen.writeln(f"if {matched_var}:")
                with gen.block():
                    gen.writeln(f"{pairs_var}.append({pair})")
                gen.writeln(f"return {matched_var}")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(self.name, expressions[0], self.modifier, self.doc)


class GrammarRule(Rule):
    """A named grammar rule."""


class BuiltInRule(Rule):
    """The base class for all built-in rules."""

    def __str__(self) -> str:
        return self.name

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python source code that implements this grammar expression."""
        # XXX: bit of a hack
        if self.name == "EOI":
            super().generate(gen, matched_var, pairs_var)
        else:
            self.expression.generate(gen, matched_var, pairs_var)
