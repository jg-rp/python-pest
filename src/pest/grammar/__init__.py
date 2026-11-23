from collections.abc import Mapping

from .expression import Expression, RegexExpression
from .expressions.choice import Choice
from .expressions.group import Group
from .expressions.postfix import (
    Optional,
    Repeat,
    RepeatExact,
    RepeatMax,
    RepeatMin,
    RepeatMinMax,
    RepeatOnce,
)
from .expressions.prefix import NegativePredicate
from .expressions.sequence import Sequence
from .expressions.terminals import CIString, Identifier, Range, SkipUntil, String
from .parser import Parser
from .rule import GrammarRule, Rule
from .scanner import Scanner, tokenize
from .tokens import Token, TokenKind

__all__ = (
    "Choice",
    "Expression",
    "Parser",
    "GrammarRule",
    "Identifier",
    "NegativePredicate",
    "Repeat",
    "Rule",
    "Sequence",
    "Scanner",
    "SkipUntil",
    "Token",
    "TokenKind",
    "parse",
    "tokenize",
    "String",
    "CIString",
    "Group",
    "RepeatMax",
    "RepeatMin",
    "RepeatOnce",
    "RepeatMinMax",
    "RepeatExact",
    "Optional",
    "RegexExpression",
    "Range",
)


def parse(
    grammar: str, builtins: Mapping[str, Rule]
) -> tuple[dict[str, GrammarRule], list[str]]:
    """Parse a pest grammar.

    Returns:
        A (rules, grammar doc) tuple.
    """
    return Parser(tokenize(grammar), builtins).parse()
