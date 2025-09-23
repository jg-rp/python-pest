"""Regex-backed expression with lazily compiled pattern."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator
from typing import Self

import regex as re

from pest.grammar.expression import Expression
from pest.grammar.expression import Success
from pest.grammar.expression import Terminal

if TYPE_CHECKING:
    from pest.state import ParserState


class RegexAtom:
    """An atomic unit of a regex sequence."""

    __slots__ = ("consumes", "quantifier")

    def __init__(self, quantifier: str | None, *, consumes: bool):
        self.consumes = consumes
        self.quantifier = quantifier  # "*", "+", "?", "{m,n}", or None


class RegexLiteral(RegexAtom):  # noqa: D101
    __slots__ = ("value",)

    def __init__(self, value: str, quantifier: str | None = None):
        super().__init__(quantifier, consumes=True)
        self.value = value


class RegexRange(RegexAtom):  # noqa: D101
    __slots__ = ("start", "end")

    def __init__(self, start: str, end: str, quantifier: str | None = None):
        super().__init__(quantifier, consumes=True)
        self.start = start
        self.end = end


class RegexPredicate(RegexAtom):  # noqa: D101
    __slots__ = ("pattern", "positive")

    def __init__(self, pattern: str, *, positive: bool):
        super().__init__(None, consumes=False)
        self.positive = positive
        self.pattern = pattern


class LazyRegexExpression(Terminal):
    """Regex-backed expression with lazily compiled pattern."""

    __slots__ = ("sequence", "compiled")

    def __init__(self, sequence: list[RegexAtom] | None = None):
        super().__init__(None)
        self.sequence: list[RegexAtom] = sequence or []
        self.compiled: re.Pattern[str] | None = None

    @property
    def pattern(self) -> re.Pattern[str]:
        """The compiled regex."""
        if self.compiled is None:
            self.compiled = re.compile(self._build_pattern(), re.VERSION1)
        return self.compiled

    def _build_pattern(self) -> str:
        parts: list[str] = []
        for atom in self.sequence:
            if isinstance(atom, RegexLiteral):
                s = re.escape(atom.value)
            elif isinstance(atom, RegexRange):
                s = f"[{atom.start}-{atom.end}]"
            elif isinstance(atom, RegexPredicate):
                s = f"(?{'=' if atom.positive else '!'}{atom.pattern})"
            else:
                raise TypeError(atom)

            if atom.quantifier:
                s += atom.quantifier
            parts.append(s)
        return "".join(parts)

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
