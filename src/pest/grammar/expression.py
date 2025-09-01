"""Abstract base class for all grammar expressions."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Iterator
from typing import NamedTuple

if TYPE_CHECKING:
    from pest.node import Node
    from pest.state import ParserState


class Success(NamedTuple):
    """A successful parse of an expression."""

    node: Node | None
    pos: int


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

    def tag_str(self) -> str:
        """Return a string representation of this expressions tag."""
        return f"{self.tag} = " if self.tag else ""

    # TODO: def children() -> list[Expression]
