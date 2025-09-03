"""Abstract base class for all grammar expressions."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Iterator
from typing import NamedTuple

from typing_extensions import Self

if TYPE_CHECKING:
    from pest.pairs import Pair
    from pest.state import ParserState


class Success(NamedTuple):
    """A successful parse of an expression."""

    pair: Pair | None
    pos: int


class Expression(ABC):
    """Abstract base class for all grammar expressions.

    In this implementation, an expression is any construct that can appear on
    the right-hand side of a grammar rule. Expressions include terminals (e.g.
    string literals, character classes), rule references, and composed forms
    such as sequences, choices, repetitions, or predicates. Modifiers like
    silent (`_`), atomic (`@`, `^`), or case-insensitive literals are also
    represented as expressions.

    A rule binds a name to a single top-level Expression.
    """

    __slots__ = ("tag",)

    def __init__(self, tag: str | None = None):
        self.tag = tag

    @abstractmethod
    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Yield instances of `Success` for each parsed node.
        Yield nothing if parsing fails.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """

    @abstractmethod
    def children(self) -> list[Expression]:
        """Return this expressions children."""

    @abstractmethod
    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""

    def tag_str(self) -> str:
        """Return a string representation of this expressions tag."""
        return f"{self.tag} = " if self.tag else ""


class Terminal(Expression):
    """Base class for terminal expressions."""

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.tag == other.tag

    def __hash__(self) -> int:
        return hash((self.__class__, self.tag))

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert not expressions
        return self
