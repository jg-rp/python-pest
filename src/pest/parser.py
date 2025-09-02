"""A pest grammar."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import PestParserError
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

    def __init__(self, rules: dict[str, Rule], doc: list[str] | None = None):
        self.rules = rules
        self.doc = doc
        # TODO: built-in rules
        # All built-in rules are silent
        # - PEEK_ALL

    def __str__(self) -> str:
        doc = "".join(f"//!{line}\n" for line in self.doc) + "\n" if self.doc else ""
        return doc + "\n\n".join(str(rule) for rule in self.rules.values())

    def parse(self, rule: str, input_: str) -> Pairs:
        """Parse `input_` starting from `rule`."""
        state = ParserState(input_, self)
        results = list(self.rules[rule].parse(state, 0))
        if results:
            return Pairs([result.pair for result in results if result.pair])

        raise PestParserError(f"could not parse input for rule {rule!r}")
