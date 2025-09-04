"""Miscellaneous built-in rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

import regex as re
from typing_extensions import Self

from pest.grammar.expression import Expression
from pest.grammar.expression import Success

if TYPE_CHECKING:
    from pest.state import ParserState


class BaseASCIIRule(Expression):
    """Base class for built-in rules matching an ASCII character."""

    RE: re.Pattern[str]

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.RE.pattern == other.RE.pattern
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.RE.pattern, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        if match := self.RE.match(state.input, start):
            yield Success(None, match.end())

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, _expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self


class ASCIIDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'9'."""

    RE = re.compile(r"[0-9]")

    def __str__(self) -> str:
        return "ASCII_DIGIT"


class ASCIINonZeroDigit(BaseASCIIRule):
    """A built-in rule matching '1'..'9'."""

    RE = re.compile(r"[1-9]")

    def __str__(self) -> str:
        return "ASCII_NONZERO_DIGIT"


class ASCIIBinDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'1'."""

    RE = re.compile(r"[0-1]")

    def __str__(self) -> str:
        return "ASCII_BIN_DIGIT"


class ASCIIOctDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'7'."""

    RE = re.compile(r"[0-7]")

    def __str__(self) -> str:
        return "ASCII_OCT_DIGIT"


class ASCIIHexDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'9' | 'a'..'f' | 'A'..'F'."""

    RE = re.compile(r"[0-9a-fA-F]")

    def __str__(self) -> str:
        return "ASCII_HEX_DIGIT"


class Newline(BaseASCIIRule):
    r"""A built-in rule matching "\n" | "\r\n" | "\r"."""

    RE = re.compile(r"\r?\n|\r")

    def __str__(self) -> str:
        return "NEWLINE"


# TODO: ASCII_ALPHANUMERIC
# TODO: ASCII
# TODO: ASCII_ALPHA_LOWER
# TODO: ASCII_ALPHA_UPPER
# TODO: ASCII_ALPHA
