"""A pest grammar."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import PestParserError
from .grammar import parse
from .grammar.expressions.choice import Choice
from .grammar.rules.ascii import ASCIIDigit
from .grammar.rules.ascii import Newline
from .grammar.rules.soi import EOI
from .grammar.rules.soi import SOI
from .grammar.rules.special import Any
from .pairs import Pairs
from .state import ParserState

if TYPE_CHECKING:
    from .grammar.expression import Expression
    from .grammar.expressions import Rule


class Parser:
    """A pest generated parser.

    Attributes:
        rules: A mapping of rule names to `Rule` instances.
        doc: An optional list of `GRAMMAR_DOC` lines.
    """

    __slots__ = ("rules", "doc")

    # TODO: built-in rules
    # All built-in rules are silent
    # - PEEK_ALL
    # TODO: what happens if a grammar redefines a built-in rule?
    BUILTIN = {
        "ANY": Any(),
        "ASCII_DIGIT": ASCIIDigit(),
        "NEWLINE": Newline(),
        "SOI": SOI(),
        "EOI": EOI(),
    }

    def __init__(self, rules: dict[str, Rule], doc: list[str] | None = None):
        self.rules = {**rules, **self.BUILTIN}
        self.doc = doc

    @classmethod
    def from_grammar(cls, grammar: str) -> Parser:
        """Parse `grammar` and return a new Parser for it."""
        return cls(*parse(grammar))

    def __str__(self) -> str:
        doc = "".join(f"//!{line}\n" for line in self.doc) + "\n" if self.doc else ""
        return doc + "\n\n".join(str(rule) for rule in self.rules.values())

    def parse(self, rule: str, input_: str) -> Pairs:
        """Parse `input_` starting from `rule`."""
        state = ParserState(self, input_)
        results = list(self.rules[rule].parse(state, 0))
        if results:
            return Pairs([result.pair for result in results if result.pair])

        assert state.failed_expr
        raise PestParserError(
            self._failure_message(
                input_,
                state.failed_expr,
                state.failed_pos,
            )
        )

    def _failure_message(self, input_: str, expr: Expression, pos: int) -> str | None:
        """Generate a human-readable error message for the furthest failure."""
        # TODO: better line break detection
        line = input_.count("\n", 0, pos) + 1
        last_nl = input_.rfind("\n", 0, pos)
        col = pos + 1 if last_nl == -1 else pos - last_nl

        found = input_[pos : pos + 10] or "end of input"

        expected = self._expected_set(expr)
        if len(expected) == 1:
            expected_str = expected[0]
        else:
            expected_str = " or ".join(expected)

        return f"error at {line}:{col}, expected {expected_str}, found {found!r}"

    def _expected_set(self, expr: Expression) -> list[str]:
        """Return a flattened list of expected alternatives for an expression."""
        if isinstance(expr, Choice):
            # Recursively flatten nested choices
            return self._expected_set(expr.left) + self._expected_set(expr.right)
        return [str(expr)]
