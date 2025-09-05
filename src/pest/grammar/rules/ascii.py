"""Built-in ASCII rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from typing_extensions import Self

from pest.grammar.expressions.lazy_regex import LazyRegexExpression
from pest.grammar.expressions.rule import Rule

if TYPE_CHECKING:
    from pest.grammar.expression import Expression
    from pest.grammar.expression import Success
    from pest.state import ParserState


class BaseASCIIRule(Rule):
    """Base class for built-in rules matching an ASCII character."""

    PATTERN: str

    def __init__(self) -> None:
        super().__init__(
            self.__class__.__name__,
            LazyRegexExpression([self.PATTERN]),
            "_",
            None,
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.expression == other.expression
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.expression, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        yield from state.parse(self.expression, start)

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, _expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self


class ASCIIDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'9'."""

    PATTERN = r"[0-9]"

    def __str__(self) -> str:
        return "ASCII_DIGIT"


class ASCIINonZeroDigit(BaseASCIIRule):
    """A built-in rule matching '1'..'9'."""

    PATTERN = r"[1-9]"

    def __str__(self) -> str:
        return "ASCII_NONZERO_DIGIT"


class ASCIIBinDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'1'."""

    PATTERN = r"[0-1]"

    def __str__(self) -> str:
        return "ASCII_BIN_DIGIT"


class ASCIIOctDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'7'."""

    PATTERN = r"[0-7]"

    def __str__(self) -> str:
        return "ASCII_OCT_DIGIT"


class ASCIIHexDigit(BaseASCIIRule):
    """A built-in rule matching '0'..'9' | 'a'..'f' | 'A'..'F'."""

    PATTERN = r"[0-9a-fA-F]"

    def __str__(self) -> str:
        return "ASCII_HEX_DIGIT"


class Newline(BaseASCIIRule):
    r"""A built-in rule matching "\n" | "\r\n" | "\r"."""

    PATTERN = r"\r?\n|\r"

    def __str__(self) -> str:
        return "NEWLINE"


# TODO: ASCII_ALPHANUMERIC
# TODO: ASCII
# TODO: ASCII_ALPHA_LOWER
# TODO: ASCII_ALPHA_UPPER
# TODO: ASCII_ALPHA
