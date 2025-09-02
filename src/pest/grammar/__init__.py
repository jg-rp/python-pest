from .expression import Expression
from .expressions.rule import Rule
from .parser import Parser
from .scanner import Scanner
from .scanner import tokenize
from .tokens import Token
from .tokens import TokenKind

__all__ = (
    "Expression",
    "Parser",
    "Rule",
    "Scanner",
    "Token",
    "TokenKind",
    "parse",
    "tokenize",
)


def parse(grammar: str) -> tuple[dict[str, Rule], list[str]]:
    """Parse a pest grammar.

    Returns:
        A (rules, grammar doc) tuple.
    """
    return Parser(tokenize(grammar)).parse()
