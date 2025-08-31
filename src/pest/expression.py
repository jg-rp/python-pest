"""Abstract base class for all grammar expressions."""

from abc import ABC
from abc import abstractmethod

from .node import Node
from .state import ParserState
from .tokens import Token


class Expression(ABC):
    """Abstract base class for all grammar expressions.

    In this implementation, an expression is any construct that can
    appear on the right-hand side of a grammar rule. Expressions
    include terminals (e.g. string literals, character classes),
    rule references, and composed forms such as sequences, choices,
    repetitions, or predicates. Modifiers like silent (`_`), atomic
    (`@`, `^`), or case-insensitive literals are also represented
    as expressions.

    A rule binds a name to a single top-level Expression.
    """

    __slots__ = ("tag",)

    def __init__(self, tag: Token | None = None):
        self.tag = tag

    @abstractmethod
    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.

        Returns:
            If parsing succeeds, a `Node` representing the result of the
            matched expression and any child expressions. Or `None` if the
            expression fails to match at `pos`.
        """
