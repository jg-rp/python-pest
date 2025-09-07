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

# TODO: update me


class LazyRegexExpression(Terminal):
    """Regex-backed expression with lazily compiled pattern."""

    __slots__ = ("_positives", "_negatives", "_compiled", "tag")

    def __init__(
        self,
        positives: list[str] | None = None,
        negatives: list[str] | None = None,
        tag: str | None = None,
    ):
        super().__init__(tag)
        self._positives = positives or []
        self._negatives = negatives or []
        self._compiled: re.Pattern[str] | None = None

    def __str__(self) -> str:
        return f"/{self.pattern.pattern}/"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self._positives == other._positives
            and self._negatives == other._negatives
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.__class__,
                tuple(self._positives),
                tuple(self._negatives),
                self.tag,
            )
        )

    def with_positive(self, regex: str) -> Self:
        """Return a RegexExpression with an extra positive alternative."""
        if self._compiled is None:
            self._positives.append(regex)
            return self
        return self.__class__(self._positives + [regex], self._negatives, self.tag)

    def with_negative(self, regex: str) -> Self:
        """Return a RegexExpression with an extra negative lookahead."""
        if self._compiled is None:
            self._negatives.append(regex)
            return self
        return self.__class__(self._positives, self._negatives + [regex], self.tag)

    @property
    def pattern(self) -> re.Pattern[str]:
        """The compiled regular expression pattern."""
        if self._compiled is None:
            pat = self._build_pattern()
            self._compiled = re.compile(pat)
        return self._compiled

    def _build_pattern(self) -> str:
        if self._positives:
            pos_pat = "|".join(self._positives)
        else:
            pos_pat = "."

        if self._negatives:
            neg_pat = "".join(f"(?!{n})" for n in self._negatives)
        else:
            neg_pat = ""

        return f"{neg_pat}(?:{pos_pat})"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        if match := self.pattern.match(state.input, start):
            yield Success(None, match.end())

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, _expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self
