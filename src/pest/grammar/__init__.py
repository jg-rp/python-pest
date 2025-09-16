from typing import Mapping

from .expression import Expression
from .expressions.postfix import Repeat
from .expressions.prefix import NegativePredicate
from .expressions.rule import GrammarRule
from .expressions.rule import Rule
from .expressions.sequence import Sequence
from .expressions.terminals import Identifier
from .parser import Parser
from .scanner import Scanner
from .scanner import tokenize
from .tokens import Token
from .tokens import TokenKind

__all__ = (
    "Expression",
    "Parser",
    "GrammarRule",
    "Identifier",
    "NegativePredicate",
    "Repeat",
    "Rule",
    "Sequence",
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
