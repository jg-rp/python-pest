"""A pest generated parser."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import PestParserError
from .grammar import parse
from .grammar.rules.ascii import ASCIIBinDigit

# TODO: Move this to grammar/rules/__init__.py
from .grammar.rules.ascii import ASCIIDigit
from .grammar.rules.ascii import ASCIIHexDigit
from .grammar.rules.ascii import ASCIINonZeroDigit
from .grammar.rules.ascii import ASCIIOctDigit
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
        "ASCII_NONZERO_DIGIT": ASCIINonZeroDigit(),
        "ASCII_BIN_DIGIT": ASCIIBinDigit(),
        "ASCII_OCT_DIGIT": ASCIIOctDigit(),
        "ASCII_HEX_DIGIT": ASCIIHexDigit(),
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

        raise PestParserError(state.failure_message())
