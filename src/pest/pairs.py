"""A `Token` and `Pairs` interface to our internal `Node` data structure."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator
from typing import NamedTuple

if TYPE_CHECKING:
    from .grammar.expressions.rule import Rule


class Token:
    """User-facing token stream element (start or end of a rule).

    Arguments:
        rule: name of the matched rule.
        pos: start position in Unicode code points.
    """

    __slots__ = ("rule", "pos")

    def __init__(self, rule: Rule, pos: int) -> None:
        self.rule = rule
        self.pos = pos


class Start(Token):
    """A token indicating the start of a rule."""

    def __repr__(self) -> str:
        return f"Start(rule={self.rule.name!r}, pos={self.pos})"


class End(Token):
    """A token indicating the end of a rule."""

    def __repr__(self) -> str:
        return f"End(rule={self.rule.name!r}, pos={self.pos})"


class Span(NamedTuple):
    """A half-open interval [start, end) into the input string."""

    start: int
    end: int

    def text(self, source: str) -> str:
        """Return the slice of the source corresponding to this span."""
        return source[self.start : self.end]


class Pair:
    __slots__ = ("rule", "start", "end", "children", "tag")

    def __init__(
        self,
        start: int,
        end: int,
        rule: Rule,
        children: list[Pair] | None = None,
        tag: str | None = None,
    ):
        self.rule = rule
        self.start = start
        self.end = end
        self.children = children or []
        self.tag = tag

    # XXX: __str__
    # TODO: get input from rule.parser?
    # or store input on Pair?

    def as_str(self, input_: str) -> str:
        return input_[self.start : self.end]

    # TODO: __iter__

    def inner(self) -> Pairs:
        return Pairs(self.children)

    def tokens(self) -> Iterator[Token]:
        yield Start(self.rule, self.start)
        for child in self.children:
            yield from child.tokens()
        yield End(self.rule, self.end)

    def span(self) -> Span:
        """Return the (start, end) span of this node as a named tuple."""
        return Span(self.start, self.end)


class Pairs:
    """An iterable over instances of `Pair`."""

    __slots__ = ("_pairs",)

    def __init__(self, pairs: list[Pair]):
        self._pairs = pairs

    def __iter__(self) -> Iterator[Pair]:
        yield from self._pairs

    def tokens(self) -> Iterator["Token"]:
        for pair in self._pairs:
            yield from pair.tokens()
