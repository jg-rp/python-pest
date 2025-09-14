"""Pest grammar tokens."""

from enum import Enum
from enum import auto
from typing import NamedTuple


class TokenKind(Enum):
    """pest grammar tokens."""

    SOI = auto()
    EOI = auto()
    ERROR = auto()

    WHITESPACE = auto()
    COMMENT_TEXT = auto()
    IDENTIFIER = auto()
    ASSIGN_OP = auto()  # =
    MODIFIER = auto()  # _, @, $, !
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    CHOICE_OP = auto()  # |
    SEQUENCE_OP = auto()  # ~
    TAG = auto()  # #tag
    POSITIVE_PREDICATE = auto()  # &
    NEGATIVE_PREDICATE = auto()  # !
    BLOCK_COMMENT = auto()  # /* .. */
    CHAR = auto()  # 'a' or '\u{10FFFF}' or '\x00' or '\n' etc.
    COMMA = auto()  # ,
    LINE_DOC = auto()  # //
    DROP = auto()  # DROP
    GRAMMAR_DOC = auto()  # //!
    LBRACKET = auto()  # [
    LPAREN = auto()  # (
    PEEK = auto()  # PEEK
    PEEK_ALL = auto()  # PEEK_ALL
    REPEAT_ONCE_OP = auto()  # +
    POP = auto()  # POP
    POP_ALL = auto()  # POP_ALL
    PUSH = auto()  # PUSH
    PUSH_LITERAL = auto()  # PUSH_LITERAL("a")
    OPTION_OP = auto()  # ?
    RANGE_OP = auto()  # ..
    RBRACKET = auto()  # ]
    RPAREN = auto()  # )
    RULE_DOC = auto()  # ///
    REPEAT_OP = auto()  # *
    STRING = auto()  # "abc"
    STRING_CI = auto()  # ^"abc"
    NUMBER = auto()  # 123
    INTEGER = auto()  # 123 or -123


class Token(NamedTuple):
    """A pest grammar token."""

    kind: TokenKind
    value: str
    start: int
    grammar: str

    def __str__(self) -> str:
        line, col = self.position()
        return f"Token({self.kind}, {self.value!r}, {line}:{col})"

    def position(self) -> tuple[int, int]:
        """Return the line and column number for the start of this token."""
        line_number = self.grammar.count("\n", 0, self.start) + 1
        column_number = self.start - self.grammar.rfind("\n", 0, self.start)
        return (line_number, column_number - 1)
