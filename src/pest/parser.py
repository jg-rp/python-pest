"""A pest generated parser."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from .exceptions import PestParsingError
from .grammar import parse

# TODO: Move this to grammar/rules/__init__.py
# TODO: unicode rules
from .grammar.rules.ascii import ASCII_RULES
from .grammar.rules.special import EOI
from .grammar.rules.special import SOI
from .grammar.rules.special import Any
from .pairs import Pairs
from .state import ParserState

if TYPE_CHECKING:
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
    BUILTIN: dict[str, Rule] = {
        "ANY": Any(),
        **ASCII_RULES,
        "SOI": SOI(),
        "EOI": EOI(),
    }

    def __init__(self, rules: Mapping[str, Rule], doc: list[str] | None = None):
        # Built-in rules overwrite grammar defined rules.
        self.rules: dict[str, Rule] = {**rules, **self.BUILTIN}
        self.doc = doc

    @classmethod
    def from_grammar(cls, grammar: str) -> Parser:
        """Parse `grammar` and return a new Parser for it."""
        rules, doc = parse(grammar, cls.BUILTIN)
        return cls(rules, doc)

    # for name, rule in grammar.rules.items():
    #     grammar.rules[name].expression = registry.optimize(rule.expression)

    def __str__(self) -> str:
        doc = "".join(f"//!{line}\n" for line in self.doc) + "\n" if self.doc else ""
        return doc + "\n\n".join(str(rule) for rule in self.rules.values())

    def parse(self, rule: str, input_: str) -> Pairs:
        """Parse `input_` starting from `rule`."""
        state = ParserState(self, input_)
        results = list(self.rules[rule].parse(state, 0))
        if results:
            return Pairs([result.pair for result in results if result.pair])

        raise PestParsingError(state.failure_message())
