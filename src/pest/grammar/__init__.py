from collections.abc import Mapping

from .expression import Expression
from .expression import RegexExpression
from .expressions.choice import Choice
from .expressions.group import Group
from .expressions.postfix import Optional
from .expressions.postfix import Repeat
from .expressions.postfix import RepeatExact
from .expressions.postfix import RepeatMax
from .expressions.postfix import RepeatMin
from .expressions.postfix import RepeatMinMax
from .expressions.postfix import RepeatOnce
from .expressions.prefix import NegativePredicate
from .expressions.sequence import Sequence
from .expressions.terminals import CIString
from .expressions.terminals import Identifier
from .expressions.terminals import Range
from .expressions.terminals import SkipUntil
from .expressions.terminals import String
from .parser import Parser
from .rule import GrammarRule
from .rule import Rule
from .scanner import Scanner
from .scanner import tokenize
from .tokens import Token
from .tokens import TokenKind

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
