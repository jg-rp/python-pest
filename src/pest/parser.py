"""A pest generated parser."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from .exceptions import PestParsingError
from .grammar import parse
from .grammar.optimizer import Optimizer
from .grammar.optimizer import OptimizerStep
from .grammar.optimizer import PassDirection
from .grammar.optimizers.skippers import skip
from .grammar.rules.ascii import ASCII_RULES
from .grammar.rules.special import EOI
from .grammar.rules.special import SOI
from .grammar.rules.special import Any
from .grammar.rules.unicode import UNICODE_RULES
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

    BUILTIN: dict[str, Rule] = {
        "ANY": Any(),
        **ASCII_RULES,
        **UNICODE_RULES,
        "SOI": SOI(),
        "EOI": EOI(),
    }

    def __init__(self, rules: Mapping[str, Rule], doc: list[str] | None = None):
        # Built-in rules overwrite grammar defined rules.
        self.rules: dict[str, Rule] = {**self.BUILTIN, **rules}
        self.doc = doc

        optimizer = Optimizer(
            self.rules,
            [OptimizerStep("skip", skip, PassDirection.PREORDER)],
            # debug=True,
        )

        for name, rule in rules.items():
            self.rules[name].expression = optimizer.optimize(rule.expression)

        # for s in optimizer.log:
        #     print(s)

    @classmethod
    def from_grammar(cls, grammar: str) -> Parser:
        """Parse `grammar` and return a new Parser for it."""
        rules, doc = parse(grammar, cls.BUILTIN)

        # TODO: validate rules
        # - validate_repetition
        # - validate_choices
        # - validate_whitespace_comment
        # - validate_tag_silent_rules

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
