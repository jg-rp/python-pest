from __future__ import annotations

from typing import TYPE_CHECKING

from ._parse import Parse
from .exceptions import PestParsingError
from .grammar import (
    BUILTIN_RULES,
    Grammar,
    serialize_expression,
    tree_view,
)
from .pairs import Pair, Pairs

if TYPE_CHECKING:
    from .grammar._ast import Rule


class Parser:
    __slots__ = ("doc", "rules")

    def __init__(self, rules: dict[str, Rule], doc: list[str]):
        self.rules = rules
        self.doc = doc

    @classmethod
    def from_grammar(cls, grammar: str) -> Parser:
        """Parse a grammar definition and return a new `Parser` for it.

        Args:
            grammar: The grammar definition as a string.

        Returns:
            Parser: A new parser instance for the given grammar.

        Raises:
            PestGrammarSyntaxError: If `grammar` is invalid.
        """
        rules, doc = Grammar.parse(grammar)
        return cls({**BUILTIN_RULES, **rules}, doc)

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
        pairs: list[Pair] = []
        parse = Parse(self.rules, text, start_pos)
        if not parse.parse_rule(self.rules[start_rule], pairs):
            raise PestParsingError(
                source=text,
                furthest_pos=parse.furthest_pos,
                furthest_expected=parse.furthest_expected,
                furthest_unexpected=parse.furthest_unexpected,
                furthest_stack=parse.furthest_stack,
            )
        return Pairs(pairs)

    def __str__(self) -> str:
        doc = "".join(f"//!{line}\n" for line in self.doc) + "\n" if self.doc else ""
        return doc + "\n\n".join(
            serialize_expression(rule) for rule in self.rules.values()
        )

    def tree_view(self) -> str:
        """Return a tree view for each rule in this grammar.

        Returns:
            str: A string representation of the grammar's rule tree.
        """
        trees = [
            tree_view(rule)
            for rule in self.rules.values()
            if rule[2] not in BUILTIN_RULES
        ]
        return "\n\n".join(trees)
