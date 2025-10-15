"""A pest grammar tree.

This module provides the `Parser` class representing rules in a pest grammar,
as well as utilities for generating parser source code and inspecting grammar rules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import PestParsingError
from .grammar import parse
from .grammar.codegen.generate import generate_module
from .grammar.optimizer import DEFAULT_OPTIMIZER
from .grammar.rule import BuiltInRule
from .grammar.rules.ascii import ASCII_RULES
from .grammar.rules.special import EOI
from .grammar.rules.special import SOI
from .grammar.rules.special import Any
from .grammar.rules.unicode import UNICODE_RULES
from .pairs import Pairs
from .state import ParserState

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .grammar.optimizer import Optimizer
    from .grammar.rule import Rule
    from .pairs import Pair


class Parser:
    """A pest parser.

    This class provides methods to parse text using a pest grammar, generate parser
    source code, and inspect the grammar tree.

    Args:
        rules: Mapping of rule names to `Rule` objects.
        doc: Optional list of grammar documentation lines.
        optimizer: Optional optimizer to apply to the rules.
        debug: If True, enables debug output during optimization.

    Attributes:
        rules: A mapping of rule names to `Rule` instances, including built-ins.
        doc: An optional list of grammar documentation lines.
    """

    BUILTIN: dict[str, Rule] = {
        "ANY": Any(),
        **ASCII_RULES,
        **UNICODE_RULES,
        "SOI": SOI(),
        "EOI": EOI(),
    }

    def __init__(
        self,
        rules: Mapping[str, Rule],
        doc: list[str] | None = None,
        *,
        optimizer: Optimizer | None = None,
        debug: bool = False,
    ):
        # Built-in rules overwrite grammar defined rules.
        self.rules: dict[str, Rule] = {**self.BUILTIN, **rules}
        self.doc = doc
        if optimizer:
            optimizer.optimize(self.rules, debug=debug)

    @classmethod
    def from_grammar(
        cls,
        grammar: str,
        *,
        optimizer: Optimizer | None = DEFAULT_OPTIMIZER,
        debug: bool = False,
    ) -> Parser:
        """Parse a grammar definition and return a new `Parser` for it.

        Args:
            grammar: The grammar definition as a string.
            optimizer: Optional optimizer to apply to the rules.
            debug: If True, enables debug output during optimization.

        Returns:
            Parser: A new parser instance for the given grammar.

        Raises:
            PestGrammarSyntaxError: If `grammar` is invalid.
        """
        rules, doc = parse(grammar, cls.BUILTIN)

        # TODO: validate rules
        # - validate_repetition
        # - validate_choices
        # - validate_whitespace_comment
        # - validate_tag_silent_rules

        return cls(rules, doc, optimizer=optimizer, debug=debug)

    def __str__(self) -> str:
        doc = "".join(f"//!{line}\n" for line in self.doc) + "\n" if self.doc else ""
        return doc + "\n\n".join(str(rule) for rule in self.rules.values())

    def parse(self, start_rule: str, text: str, *, start_pos: int = 0) -> Pairs:
        """Parse `text` starting from the specified `start_rule`.

        Args:
            start_rule: The name of the rule to start parsing from.
            text: The input string to parse.
            start_pos: The position in the input string to start parsing from
                (default: 0).

        Returns:
            Pairs: The parse tree as a `Pairs` object.

        Raises:
            KeyError: If `start_rule` is not a valid rule name.
            PestParsingError: If the input `text` cannot be parsed according to the
                grammar.
        """
        rule = self.rules[start_rule]
        state = ParserState(text, start_pos, self)
        pairs: list[Pair] = []
        matched = rule.parse(state, pairs)

        if matched:
            return Pairs(pairs)

        raise PestParsingError(state)

    def generate(self) -> str:
        """Return a generated parser as Python module source code.

        Returns:
            str: The generated Python source code for the parser.
        """
        return generate_module(self.rules)

    def tree_view(self) -> str:
        """Return a tree view for each non-built-in rule in this grammar.

        Returns:
            str: A string representation of the grammar's rule tree.
        """
        trees = [
            rule.tree_view()
            for rule in self.rules.values()
            if not isinstance(rule, BuiltInRule)
        ]
        return "\n\n".join(trees)
