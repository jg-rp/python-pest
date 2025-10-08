"""A `Token` and `Pairs` interface to our internal `Node` data structure."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import overload

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .grammar.codegen.state import RuleFrame
    from .grammar.rule import Rule


class Token:
    """User-facing token stream element (start or end of a rule).

    Arguments:
        rule: name of the matched rule.
        pos: start position in Unicode code points.
    """

    __slots__ = ("rule", "pos")

    def __init__(self, rule: Rule | RuleFrame, pos: int) -> None:
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

    text: str
    start: int
    end: int

    def __str__(self) -> str:
        return self.text[self.start : self.end]

    def as_str(self) -> str:
        """Return the slice of the source corresponding to this span."""
        return str(self)

    def end_pos(self) -> Position:
        """Return this span's end position."""
        return Position(self.text, self.end)

    def start_pos(self) -> Position:
        """Return this span's start position."""
        return Position(self.text, self.start)

    def split(self) -> tuple[Position, Position]:
        """Return a tuple of start position and end position."""
        return self.start_pos(), self.end_pos()

    def lines(self) -> list[str]:
        """Return a list of lines covered by this span.

        Includes lines that are partially covered.
        """
        lines = self.text.splitlines(keepends=True)
        start_line_number, _ = self.start_pos().line_col()
        end_line_number, _ = self.end_pos().line_col()
        return lines[start_line_number - 1 : end_line_number]


class Position(NamedTuple):
    """A position in a string as a Unicode codepoint offset."""

    text: str
    pos: int

    def line_col(self) -> tuple[int, int]:
        """Return the line an column number of this position."""
        lines = self.text.splitlines(keepends=True)
        cumulative_length = 0
        target_line_index = -1

        for i, line in enumerate(lines):
            cumulative_length += len(line)
            if self.pos < cumulative_length:
                target_line_index = i
                break

        if target_line_index == -1:
            return len(lines) + 1, 1

        # 1-based
        line_number = target_line_index + 1
        column_number = (
            self.pos - (cumulative_length - len(lines[target_line_index])) + 1
        )
        return line_number, column_number

    def line_of(self) -> str:
        """Return the line of text that contains this position."""
        line_number, _ = self.line_col()
        return self.text[line_number - 1]


class Pair:
    """A matching pair of Tokens and everything between them."""

    __slots__ = ("children", "end", "input", "name", "rule", "start", "tag")
    __match_args__ = ("name", "children", "start", "end")

    def __init__(
        self,
        input_: str,
        start: int,
        end: int,
        rule: Rule | RuleFrame,
        children: list[Pair] | None = None,
        tag: str | None = None,
    ):
        self.input = input_
        self.rule = rule
        self.start = start
        self.end = end
        self.children = children or []
        self.tag = tag
        self.name = rule.name

    def __str__(self) -> str:
        return self.input[self.start : self.end]

    def __repr__(self) -> str:
        return f"Pair(rule={self.name!r}, text={str(self)!r}, tag={self.tag!r})"

    def as_str(self) -> str:
        """Return the substring pointed to by this token pair."""
        return str(self)

    def __iter__(self) -> Iterator[Pair]:
        return iter(self.children)

    def inner(self) -> Pairs:
        """Return inner pairs between this token pair."""
        return Pairs(self.children)

    def stream(self) -> Stream:
        """Return inner pairs as a stream."""
        return Pairs(self.children).stream()

    def tokens(self) -> Iterator[Token]:
        """Yield start and end tokens for this pair and any children in between."""
        yield Start(self.rule, self.start)
        for child in self.children:
            yield from child.tokens()
        yield End(self.rule, self.end)

    def span(self) -> Span:
        """Return the (start, end) span of this node as a named tuple."""
        return Span(self.input, self.start, self.end)

    def dump(self) -> dict[str, object]:
        """Return a pest-debug-like JSON structure."""
        d: dict[str, object] = {
            "rule": self.rule.name,
            "span": {
                "str": self.input[self.start : self.end],
                "start": self.start,
                "end": self.end,
            },
            "inner": [child.dump() for child in self.children],
        }

        if self.tag is not None:
            d["node_tag"] = self.tag

        return d

    def line_col(self) -> tuple[int, int]:
        """Return the line and column number of this pair's start position."""
        return self.span().start_pos().line_col()

    @property
    def text(self) -> str:
        """The substring pointed to by this token pair."""
        return self.input[self.start : self.end]

    @property
    def inner_texts(self) -> list[str]:
        """The list of substrings pointed to by this pair's children."""
        return [str(c) for c in self.children]


class Pairs(Sequence[Pair]):
    """An iterable over instances of `Pair`."""

    __slots__ = ("_pairs",)

    def __init__(self, pairs: list[Pair]):
        self._pairs = pairs

    def __iter__(self) -> Iterator[Pair]:
        yield from self._pairs

    def __len__(self) -> int:
        return len(self._pairs)

    @overload
    def __getitem__(self, index: int) -> Pair: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Pair]: ...

    def __getitem__(self, index: int | slice) -> Pair | Sequence[Pair]:
        return self._pairs[index]

    def tokens(self) -> Iterator[Token]:
        """Yield start and end tokens for each pair."""
        for pair in self._pairs:
            yield from pair.tokens()

    def stream(self) -> Stream:
        """Return pairs as a stream that can be stepped through."""
        return Stream(self._pairs)

    def dump(self) -> list[dict[str, object]]:
        """Return list of pest-debug-like JSON dicts."""
        return [pair.dump() for pair in self._pairs]

    def flatten(self) -> Iterator[Pair]:
        """Generate a flat stream of pairs."""

        def _flatten(pair: Pair) -> Iterator[Pair]:
            yield pair
            for child in pair.children:
                yield from _flatten(child)

        for pair in self._pairs:
            yield from _flatten(pair)

    def first(self) -> Pair:
        """Return the single root pair."""
        return self[0]

    def find_first_tagged(self, label: str) -> Pair | None:
        """Finds the first pair that has its node tagged with `label`."""
        for pair in self.flatten():
            if pair.tag == label:
                return pair
        return None

    def find_tagged(self, label: str) -> Iterator[Pair]:
        """Iterate over pairs tagged with `label`."""
        return (p for p in self.flatten() if p.tag == label)


class Stream:
    """Step through pairs of tokens."""

    def __init__(self, pairs: list[Pair]):
        self.pos = 0
        self.pairs = pairs

    def next(self) -> Pair | None:
        """Return the next pair and advance the stream."""
        if self.pos < len(self.pairs):
            pair = self.pairs[self.pos]
            self.pos += 1
            return pair
        return None

    def backup(self) -> None:
        """Go back one position in the stream."""
        if self.pos > 0:
            self.pos -= 1

    def peek(self) -> Pair | None:
        """Return the next pair without advancing the stream."""
        if self.pos < len(self.pairs):
            return self.pairs[self.pos]
        return None
