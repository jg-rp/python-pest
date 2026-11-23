from importlib.metadata import version

from .exceptions import PestParsingError
from .grammar.exceptions import PestGrammarError, PestGrammarSyntaxError
from .grammar.optimizer import DEFAULT_OPTIMIZER, DEFAULT_OPTIMIZER_PASSES, Optimizer
from .grammar.rule import Rule
from .pairs import End, Pair, Pairs, Position, Span, Start, Stream, Token
from .parser import Parser
from .pratt import PrattParser
from .state import ParserState, RuleFrame

__version__ = version("python-pest")

__all__ = (
    "DEFAULT_OPTIMIZER_PASSES",
    "DEFAULT_OPTIMIZER",
    "End",
    "Optimizer",
    "Pair",
    "Pairs",
    "Parser",
    "ParserState",
    "PestGrammarError",
    "PestGrammarSyntaxError",
    "PestParsingError",
    "Position",
    "PrattParser",
    "Rule",
    "RuleFrame",
    "Span",
    "Start",
    "Stream",
    "Token",
)
