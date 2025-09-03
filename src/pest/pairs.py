"""A `Token` and `Pairs` interface to our internal `Node` data structure."""

from __future__ import annotations

from collections.abc import Iterable
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
    """A matching pair of Tokens and everything between them."""

    __slots__ = ("input", "rule", "start", "end", "children", "tag")

    def __init__(
        self,
        input_: str,
        start: int,
        end: int,
        rule: Rule,
        children: list[Pair] | None = None,
        tag: str | None = None,
    ):
        self.input = input_
        self.rule = rule
        self.start = start
        self.end = end
        self.children = children or []
        self.tag = tag

    def __str__(self) -> str:
        return self.input[self.start : self.end]

    def as_str(self) -> str:
        """Return the substring pointed to by this token pair."""
        return str(self)

    def __iter__(self) -> Iterator[Pair]:
        return iter(Pairs(self.children))

    def inner(self) -> Pairs:
        """Return inner pairs between this token pair."""
        return Pairs(self.children)

    def tokens(self) -> Iterator[Token]:
        """Yield start and end tokens for this pair and any children in between."""
        yield Start(self.rule, self.start)
        for child in self.children:
            yield from child.tokens()
        yield End(self.rule, self.end)

    def span(self) -> Span:
        """Return the (start, end) span of this node as a named tuple."""
        return Span(self.start, self.end)

    def as_dict(self) -> dict[str, object]:
        """Return a pest-debug-like JSON structure."""
        d: dict[str, object] = {
            "rule": self.rule.name,
            "span": {
                "str": self.input[self.start : self.end],
                "start": self.start,
                "end": self.end,
            },
            "inner": [child.as_dict() for child in self.children],
        }

        if self.tag is not None:
            d["node_tag"] = self.tag

        return d


class Pairs(Iterable[Pair]):
    """An iterable over instances of `Pair`."""

    __slots__ = ("_pairs",)

    def __init__(self, pairs: list[Pair]):
        self._pairs = pairs

    def __iter__(self) -> Iterator[Pair]:
        yield from self._pairs

    def tokens(self) -> Iterator["Token"]:
        """Yield start and end tokens for each pair."""
        for pair in self._pairs:
            yield from pair.tokens()

    def as_list(self) -> list[dict[str, object]]:
        """Return list of pest-debug-like JSON dicts."""
        return [pair.as_dict() for pair in self._pairs]
