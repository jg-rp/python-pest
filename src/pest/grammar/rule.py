"""A logical grammar rule."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterable
from typing import Iterator
from typing import Self

from pest.grammar import Expression
from pest.grammar.expression import Success
from pest.grammar.expressions.terminals import Identifier
from pest.pairs import Pair

if TYPE_CHECKING:
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

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        restore_atomic_depth = state.atomic_depth

        if self.modifier & (ATOMIC | COMPOUND):
            state.atomic_depth += 1
        elif self.modifier & NONATOMIC:
            state.atomic_depth = 0

        results = list(state.parse(self.expression, start, self.tag))

        # TODO: let ParserState restore atomic depth
        if not results:
            state.atomic_depth = restore_atomic_depth
            return

        end = results[-1].pos

        if self.modifier & SILENT:
            # Yield children without an enclosing Pair
            yield from results
        elif self.modifier & ATOMIC:
            if isinstance(self.expression, Rule):
                rule: Rule | None = self.expression
            elif isinstance(self.expression, Identifier):
                rule = state.parser.rules.get(self.expression.value)
            else:
                rule = None

            if not rule or not rule.modifier & (NONATOMIC | COMPOUND):
                # Atomic rule silences children
                yield Success(
                    Pair(
                        input_=state.input,
                        rule=self,
                        start=start,
                        end=end,
                        children=[],
                    ),
                    pos=end,
                )
            else:
                # Non-atomic child rule.
                # XXX: What about children's children?
                yield Success(
                    Pair(
                        input_=state.input,
                        rule=self,
                        start=start,
                        end=end,
                        children=[success.pair for success in results if success.pair],
                    ),
                    pos=end,
                )
        else:
            yield Success(
                Pair(
                    input_=state.input,
                    rule=self,
                    start=start,
                    end=end,
                    children=[success.pair for success in results if success.pair],
                ),
                pos=end,
            )

        # Restore atomic depth to what it was before this rule
        state.atomic_depth = restore_atomic_depth

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
