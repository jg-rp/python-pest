"""Miscellaneous built-in rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

import regex as re

from pest.grammar.expression import Expression
from pest.grammar.expression import Success

if TYPE_CHECKING:
    from pest.state import ParserState


class BaseASCIIRule(Expression):
    """Base class for built-in rules matching an ASCII character."""

    RE: re.Pattern[str]

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        if match := self.RE.match(state.input, start):
            yield Success(None, match.end())


class ASCIIDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'9'."""

    RE = re.compile(r"[0-9]")

    def __str__(self) -> str:
        return "ASCII_DIGIT"


class Newline(BaseASCIIRule):
    r"""A built-in rule matching "\n" | "\r\n" | "\r"."""

    RE = re.compile(r"\r?\n|\r")

    def __str__(self) -> str:
        return "NEWLINE"


# TODO: ASCII_ALPHANUMERIC
# TODO: ASCII
