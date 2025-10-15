from importlib.metadata import version

from .exceptions import PestParsingError
from .grammar.exceptions import PestGrammarError
from .grammar.exceptions import PestGrammarSyntaxError
from .grammar.optimizer import DEFAULT_OPTIMIZER
from .grammar.optimizer import DEFAULT_OPTIMIZER_PASSES
from .grammar.optimizer import Optimizer
from .grammar.rule import Rule
from .pairs import End
from .pairs import Pair
from .pairs import Pairs
from .pairs import Position
from .pairs import Span
from .pairs import Start
from .pairs import Stream
from .pairs import Token
from .parser import Parser
from .pratt import PrattParser
from .state import ParserState
from .state import RuleFrame

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
