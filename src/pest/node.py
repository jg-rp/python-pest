"""A Node representing a successful parse of an expression."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import NamedTuple

if TYPE_CHECKING:
    from .grammar.expressions import Rule


class Span(NamedTuple):
    """A half-open interval [start, end) into the input string."""

    start: int
    end: int

    def text(self, source: str) -> str:
        """Return the slice of the source corresponding to this span."""
        return source[self.start : self.end]


@dataclass
class Node:
    """Represents a successful parse of an expression.

    Attributes:
        start, end:
            Span of the input matched by this node (Unicode code point offsets).
        children:
            Nodes produced by sub-expressions.
        rule:
            The originating Rule, if this node corresponds to a named rule.
            Anonymous expressions usually leave this unset.
        tag:
            Optional user-specified label (from #tag syntax).
        source:
            Reference to the original input string, used to extract
            substrings for Tokens and Pairs APIs.
    """

    start: int
    end: int
    children: list[Node] = field(default_factory=list)
    rule: Rule | None = None  # forward reference
    tag: str | None = None
    source: str | None = None

    def span(self) -> Span:
        """Return the (start, end) span of this node as a named tuple."""
        return Span(self.start, self.end)

    def text(self) -> str:
        """Return the substring of the source matched by this node."""
        if self.source is None:
            raise ValueError("Node has no source reference")
        return self.source[self.start : self.end]

    def is_leaf(self) -> bool:
        """Return True if this node has no children."""
        return not self.children
