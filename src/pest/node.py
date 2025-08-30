"""A Node representing a successful parse of an expression."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import NamedTuple


class Span(NamedTuple):
    """A half-open interval [start, end) into the input string."""

    start: int
    end: int


@dataclass
class Node:
    """Represents a successful parse of an expression.

    Attributes:
        start:
            The starting input position (inclusive).
        end:
            The ending input position (exclusive).
        children:
            A list of child nodes produced by sub-expressions.
        value:
            Optional semantic value associated with this node
            (e.g. the matched literal string or a transformed value).
        name:
            The rule name that produced this node, if any. Anonymous
            expressions (like sequence or choice) usually leave this unset.
        tag:
            An optional user-specified label (from `#tag` syntax).
    """

    start: int
    end: int
    children: list[Node] = field(default_factory=list)
    value: object = None
    name: str | None = None
    tag: str | None = None

    def span(self) -> Span:
        """Return the (start, end) span of this node as a named tuple."""
        return Span(self.start, self.end)

    def is_leaf(self) -> bool:
        """Return True if this node has no children."""
        return not self.children
