"""Abstract base class for all grammar expressions."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Callable
from typing import Iterator
from typing import NamedTuple

import regex as re
from typing_extensions import Self

if TYPE_CHECKING:
    from pest.grammar.expressions.rule import Rule
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

    __slots__ = ("tag", "_pure")

    def __init__(self, tag: str | None = None):
        self.tag = tag
        self._pure: bool | None = None

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

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        if self._pure is None:
            self._pure = all(child.is_pure(rules, seen) for child in self.children())
        return self._pure

    def map_bottom_up(self, func: Callable[[Expression], Expression]) -> Expression:
        """Apply `func` in a post order tree traversal of this expression tree."""
        new_children = [c.map_bottom_up(func) for c in self.children()]
        expr = self.with_children(new_children)
        return func(expr)

    def map_top_down(self, func: Callable[[Expression], Expression]) -> Expression:
        """Apply `func` in a pre order tree traversal of this expression tree."""
        expr = func(self)
        new_children = [c.map_top_down(func) for c in expr.children()]
        return expr.with_children(new_children)

    def tree_view(self) -> str:
        """Return an ASCII tree view of this expression and its children."""
        # Collect nodes: (prefix, connector, class_name, repr_value)
        nodes = []

        def collect(
            node: Expression, prefix: str = "", *, is_last: bool = True
        ) -> None:
            connector = "" if prefix == "" else ("└── " if is_last else "├── ")
            nodes.append((prefix, connector, node.__class__.__name__, repr(str(node))))
            child_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(node.children()):
                last = i == len(node.children()) - 1
                collect(child, child_prefix, is_last=last)

        collect(self)

        # Find maximum width of the left-hand side
        widths = [len(prefix + connector + cls) for prefix, connector, cls, _ in nodes]
        max_width = max(widths) if widths else 0

        # Build aligned lines
        lines = []
        for (prefix, connector, cls, val), width in zip(nodes, widths, strict=True):
            left = prefix + connector + cls
            padding = " " * (max_width - width + 4)  # +4 for spacing column
            lines.append(left + padding + val)

        return "\n".join(lines)


class Terminal(Expression):
    """Base class for terminal expressions."""

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert not expressions
        return self


class RegexExpression(Terminal):
    """A simple terminal expression with a `pattern` and a `regex`."""

    __slots__ = ("pattern", "regex")

    def __init__(self, pattern: str):
        super().__init__()
        self.pattern = pattern
        self.regex = re.compile(pattern)

    def __str__(self) -> str:
        return f"/{self.pattern}/"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if match := self.regex.match(state.input, start):
            yield Success(None, match.end())
