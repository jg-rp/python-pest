from typing import Mapping

from .expression import Expression
from .expressions.rule import GrammarRule
from .expressions.rule import Rule
from .parser import Parser
from .scanner import Scanner
from .scanner import tokenize
from .tokens import Token
from .tokens import TokenKind

__all__ = (
    "Expression",
    "Parser",
    "GrammarRule",
    "Rule",
    "Scanner",
    "Token",
    "TokenKind",
    "parse",
    "tokenize",
)


def parse(
    grammar: str, builtins: Mapping[str, Rule]
) -> tuple[dict[str, GrammarRule], list[str]]:
    """Parse a pest grammar.

    Returns:
        A (rules, grammar doc) tuple.
    """
    return Parser(tokenize(grammar), builtins).parse()
