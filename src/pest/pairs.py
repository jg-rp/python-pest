"""A `Token` and `Pair` interface to a grammar parse tree.

This module provides classes for representing tokens, pairs, and sequences of pairs
in a grammar parse tree, as well as utilities for traversing and inspecting the tree.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import overload

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .grammar.rule import Rule
    from .state import RuleFrame


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

    __slots__ = ()

    def __repr__(self) -> str:
        return f"Start(rule={self.rule.name!r}, pos={self.pos})"


class End(Token):
    """A token indicating the end of a rule."""

    __slots__ = ()

    def __repr__(self) -> str:
        return f"End(rule={self.rule.name!r}, pos={self.pos})"


class Span(NamedTuple):
    """A half-open interval [start, end) into the input string.

    Represents a substring of the input, along with its start and end positions.
    """

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
    """A position in a string as a Unicode codepoint offset.

    Provides utilities for determining line and column numbers.
    """

    text: str
    pos: int

    def line_col(self) -> tuple[int, int]:
        """Return the line and column number of this position.

        Returns:
            A tuple (line_number, column_number), both 1-based.
        """
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
    """A matching pair of Tokens and everything between them.

    Represents a node in the parse tree, corresponding to a matched rule and its
    children.

    Args:
        input_: The input string.
        start: Start position in the input.
        end: End position in the input.
        rule: The rule or rule frame this pair represents.
        children: List of child pairs (subrules).
        tag: Optional tag for this node.
    """

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
        """Return the (start, end) span of this node."""
        return Span(self.input, self.start, self.end)

    def dump(self) -> dict[str, object]:
        """Return a pest-debug-like JSON structure representing this pair."""
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

    def dumps(self, indent: int = 0, *, new_line: bool = True) -> str:
        """Return a string representation of this token pair and all its children.

        Translated from the `format_pair` function found in the source for pest.rs.

        https://github.com/pest-parser/site/blob/master/src/lib.rs.
        """
        n = len(self.children)
        _indent = "  " * indent if new_line else ""
        dash = "- " if new_line else ""
        pair_tag = f"{self.tag} " if self.tag else ""

        children = [
            pair.dumps(indent + 1 if n > 1 else indent, new_line=n > 1)
            for pair in self.children
        ]

        if n == 0:
            return f"{_indent}{dash}{pair_tag}{self.name}: {json.dumps(self.text)}"

        if n == 1:
            return f"{_indent}{dash}{pair_tag}{self.name} > {children[0]}"

        _children = "\n".join(children)
        return f"{_indent}{dash}{pair_tag}{self.name}\n{_children}"

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
    """A sequence of token pairs.

    Provides sequence and utility methods for working with lists of Pair objects.

    Args:
        pairs: List of Pair objects.
    """

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
        """Yield start and end tokens for each pair in the sequence."""
        for pair in self._pairs:
            yield from pair.tokens()

    def stream(self) -> Stream:
        """Return pairs as a stream that can be stepped through."""
        return Stream(self._pairs)

    def dump(self) -> list[dict[str, object]]:
        """Return pairs as a JSON-like list of dicts."""
        return [pair.dump() for pair in self._pairs]

    def dumps(self, *, compact: bool = True) -> str:
        """Return a JSON formatted string representation of this node.

        Args:
            compact: If True, returns a compact string; otherwise, pretty-prints JSON.

        Returns:
            A string representation of the pairs.
        """
        if compact:
            return "\n".join(pair.dumps() for pair in self._pairs)
        return json.dumps(self.dump(), indent=2, sort_keys=False)

    def flatten(self) -> Iterator[Pair]:
        """Generate a flat iterator over all pairs and their descendants."""

        def _flatten(pair: Pair) -> Iterator[Pair]:
            yield pair
            for child in pair.children:
                yield from _flatten(child)

        for pair in self._pairs:
            yield from _flatten(pair)

    def first(self) -> Pair:
        """Return the single root pair.

        Returns:
            The first Pair in the sequence.
        """
        return self[0]

    def find_first_tagged(self, label: str) -> Pair | None:
        """Finds the first pair that has its node tagged with `label`.

        Args:
            label: The tag to search for.

        Returns:
            The first Pair with the given tag, or None if not found.
        """
        for pair in self.flatten():
            if pair.tag == label:
                return pair
        return None

    def find_tagged(self, label: str) -> Iterator[Pair]:
        """Iterate over pairs tagged with `label`.

        Args:
            label: The tag to search for.

        Returns:
            An iterator over all Pairs with the given tag.
        """
        return (p for p in self.flatten() if p.tag == label)


class Stream:
    """Step through pairs of tokens.

    Provides a simple interface for sequential access to a list of Pair objects.
    """

    __slots__ = ("pos", "pairs")

    def __init__(self, pairs: list[Pair]):
        self.pos = 0
        self.pairs = pairs

    def next(self) -> Pair | None:
        """Return the next pair and advance the stream.

        Returns:
            The next Pair, or None if at the end of the stream.
        """
        if self.pos < len(self.pairs):
            pair = self.pairs[self.pos]
            self.pos += 1
            return pair
        return None

    def backup(self) -> None:
        """Go back one position in the stream, if possible."""
        if self.pos > 0:
            self.pos -= 1

    def peek(self) -> Pair | None:
        """Return the next pair without advancing the stream.

        Returns:
            The next Pair, or None if at the end of the stream.
        """
        if self.pos < len(self.pairs):
            return self.pairs[self.pos]
        return None
