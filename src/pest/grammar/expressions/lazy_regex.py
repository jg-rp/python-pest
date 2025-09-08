"""Regex-backed expression with lazily compiled pattern."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

import regex as re
from typing_extensions import Self

from pest.grammar.expression import Expression
from pest.grammar.expression import Success
from pest.grammar.expression import Terminal

if TYPE_CHECKING:
    from pest.state import ParserState


class LazyRegexExpression(Terminal):
    """Regex-backed expression with lazily compiled pattern."""

    __slots__ = (
        "positives",
        "negatives",
        "positive_ranges",
        "negative_ranges",
        "compiled",
        "consuming",
    )

    def __init__(
        self,
        *,
        positives: list[str] | None = None,
        negatives: list[str] | None = None,
        positive_ranges: list[tuple[str, str]] | None = None,
        negative_ranges: list[tuple[str, str]] | None = None,
        consuming: bool = True,
    ) -> None:
        super().__init__(None)
        self.positives = positives or []
        self.negatives = negatives or []
        self.positive_ranges = positive_ranges or []
        self.negative_ranges = negative_ranges or []
        self.compiled: re.Pattern[str] | None = None
        self.consuming = consuming

    def __str__(self) -> str:
        return f"/{self.pattern.pattern}/"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    def with_positive(self, s: str) -> Self:
        """Return this regex expression with an additional positive pattern."""
        if self.compiled:
            expr = self._copy()
            return expr.with_positive(s)

        if len(s) == 1:
            self.positive_ranges.append((s, s))
        else:
            self.positives.append(s)
        return self

    def with_negative(self, s: str) -> Self:
        """Return this regex expression with an additional negative pattern."""
        if self.compiled:
            expr = self._copy()
            return expr.with_positive(s)

        if len(s) == 1:
            self.negative_ranges.append((s, s))
        else:
            self.negatives.append(s)
        return self

    def with_range(self, start: str, end: str) -> Self:
        """Return this regex expression with an additional positive character range."""
        if self.compiled:
            expr = self._copy()
            return expr.with_range(start, end)

        self.positive_ranges.append((start, end))
        return self

    def with_negative_range(self, start: str, end: str) -> Self:
        """Return this regex expression with an additional negative character range."""
        if self.compiled:
            expr = self._copy()
            return expr.with_negative_range(start, end)

        self.negative_ranges.append((start, end))
        return self

    @property
    def pattern(self) -> re.Pattern[str]:
        """The compiled regular expression pattern."""
        if self.compiled is None:
            try:
                self.compiled = re.compile(self._build_pattern(), re.VERSION1)
            except re.error:
                print("--", self._build_pattern())
                print("**", self.positives, self.positive_ranges)
                raise
        return self.compiled

    def _build_pattern(self) -> str:
        """Return an optimized regex pattern with simplified ranges.

        - Single-character entries are merged into ranges.
        - Multi-character positives become explicit alternations.
        - Multi-character negatives are expressed as negative lookaheads.
        """

        def merge_ranges(
            ranges: list[tuple[str, str]], chars: list[str]
        ) -> list[tuple[int, int]]:
            points = [(ord(c), ord(c)) for c in chars if len(c) == 1]
            points += [(ord(a), ord(b)) for a, b in ranges]
            if not points:
                return []
            points.sort()
            merged = []
            cur_start, cur_end = points[0]
            for start, end in points[1:]:
                if start <= cur_end + 1:
                    cur_end = max(cur_end, end)
                else:
                    merged.append((cur_start, cur_end))
                    cur_start, cur_end = start, end
            merged.append((cur_start, cur_end))
            return merged

        def build_class_and_literals(
            chars: list[str], ranges: list[tuple[str, str]]
        ) -> tuple[str, list[str]]:
            merged = merge_ranges(ranges, chars)
            parts = []
            for s, e in merged:
                if s == e:
                    parts.append(chr(s))
                else:
                    parts.append(f"{chr(s)}-{chr(e)}")
            char_class = "[" + "".join(parts) + "]" if parts else ""
            literals = [c for c in chars if len(c) > 1]
            return char_class, literals

        # Build positives and negatives
        pos_class, pos_literals = build_class_and_literals(
            self.positives, self.positive_ranges
        )

        neg_class, neg_literals = build_class_and_literals(
            self.negatives, self.negative_ranges
        )

        lookaheads = []
        if neg_literals:
            escaped = [re.escape(lit) for lit in neg_literals]
            lookaheads.append(f"(?!{'|'.join(escaped)})")

        if not pos_class and not pos_literals and not neg_class and not lookaheads:
            return "."

        # Only positives
        if pos_class and not neg_class:
            body = pos_class
            if pos_literals:
                body = f"(?:{'|'.join(sorted(pos_literals + [pos_class]))})"
            return "".join(lookaheads) + body

        if not pos_class and not neg_class and pos_literals:
            body = f"(?:{'|'.join(sorted(pos_literals))})"
            return "".join(lookaheads) + body

        # Only negatives
        if not pos_class and neg_class:
            body = neg_class.replace("[", "[^", 1)
            return "".join(lookaheads) + body

        # Both positives and negatives
        if pos_literals:
            class_part = f"[{pos_class}--{neg_class}]" if pos_class else neg_class
            body = f"(?:{'|'.join(sorted(pos_literals + [class_part]))})"
        else:
            body = f"[{pos_class}--{neg_class}]" if pos_class and neg_class else "."
        return "".join(lookaheads) + body

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        if match := self.pattern.match(state.input, start):
            yield Success(None, match.end() if self.consuming else start)

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, _expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self

    def _copy(self) -> Self:
        expr = self.__class__()
        expr.positive_ranges = self.positive_ranges[:]
        expr.positives = self.positives[:]
        expr.negative_ranges = self.negative_ranges[:]
        expr.negatives = self.negatives[:]
        return expr

    def repeat(self) -> LazyRegexExpression:
        """Return a new instance that matches this expression zero or more times."""
        expr = self._copy()
        expr.consuming = True
        expr.compiled = re.compile(f"(?:{self._build_pattern()})*", re.VERSION1)
        return expr
