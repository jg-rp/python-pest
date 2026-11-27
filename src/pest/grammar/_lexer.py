import regex as re

from ._tokens import *
from ._tokens import Token, TokenKind

P_WHITESPACE = r"[ \t\n\r]+"
P_LINE_COMMENT = r"//(?!/|!).*"
P_BLOCK_COMMENT = r"/\*(?:[^*/]|\*(?!/)|/(?!\*)|(?R))*\*/"

RE_TRIVIA = re.compile(f"(?:{P_WHITESPACE}|{P_LINE_COMMENT}|{P_BLOCK_COMMENT})+")
RE_NEWLINE = re.compile(r"\r?\n")
RE_IDENTIFIER = re.compile(r"[_a-zA-Z][_a-zA-Z0-9]*")
RE_INTEGER = re.compile(r"-?[0-9]+")
RE_CHAR = re.compile(
    r"'\\[\\\"\r\n\t\0']'|'\\x[0-9a-fA-F]{2}'|'\\u\{[0-9a-fA-F]{2,6}\}'|'[^\\']'"
)


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    length = len(source)
    pos = 0

    while pos < length:
        pos = _skip_trivia(source, pos)
        if pos >= length:
            break

        ch = source[pos]

        if ch == "&":
            tokens.append((TOKEN_AMP, pos, pos + 1))
            pos += 1
        elif ch == "=":
            tokens.append((TOKEN_ASSIGN, pos, pos + 1))
            pos += 1
        elif ch == "*":
            tokens.append((TOKEN_ASTERISK, pos, pos + 1))
            pos += 1
        elif ch == "@":
            tokens.append((TOKEN_AT, pos, pos + 1))
            pos += 1
        elif ch == "^":
            tokens.append((TOKEN_CARET, pos, pos + 1))
            pos += 1
        elif ch == ",":
            tokens.append((TOKEN_COMMA, pos, pos + 1))
            pos += 1
        elif ch == "$":
            tokens.append((TOKEN_DOLLAR, pos, pos + 1))
            pos += 1
        elif ch == "!":
            tokens.append((TOKEN_EXCLAIM, pos, pos + 1))
            pos += 1
        elif ch == "#":
            tokens.append((TOKEN_HASH, pos, pos + 1))
            pos += 1
        elif ch == "{":
            tokens.append((TOKEN_LBRACE, pos, pos + 1))
            pos += 1
        elif ch == "[":
            tokens.append((TOKEN_LBRACKET, pos, pos + 1))
            pos += 1
        elif ch == "(":
            tokens.append((TOKEN_LPAREN, pos, pos + 1))
            pos += 1
        elif ch == "|":
            tokens.append((TOKEN_PIPE, pos, pos + 1))
            pos += 1
        elif ch == "+":
            tokens.append((TOKEN_PLUS, pos, pos + 1))
            pos += 1
        elif ch == "?":
            tokens.append((TOKEN_QUESTION, pos, pos + 1))
            pos += 1
        elif ch == "}":
            tokens.append((TOKEN_RBRACE, pos, pos + 1))
            pos += 1
        elif ch == "]":
            tokens.append((TOKEN_RBRACKET, pos, pos + 1))
            pos += 1
        elif ch == ")":
            tokens.append((TOKEN_RPAREN, pos, pos + 1))
            pos += 1
        elif ch == "~":
            tokens.append((TOKEN_TILDE, pos, pos + 1))
            pos += 1
        elif ch == ".":
            if pos + 1 < length and source[pos + 1] == ".":
                tokens.append((TOKEN_DOUBLE_DOT, pos, pos + 2))
                pos += 2
            else:
                tokens.append((TOKEN_UNKNOWN, pos, pos + 1))
                pos += 1
        elif ch == "/":
            if pos + 2 < length:
                if source.startswith("//!", pos):
                    tokens.append((TOKEN_GRAMMAR_DOC, pos, pos + 3))
                    pos += 3
                elif source.startswith("///", pos):
                    tokens.append((TOKEN_RULE_DOC, pos, pos + 3))
                    pos += 3
                else:
                    tokens.append((TOKEN_UNKNOWN, pos, pos + 1))
                    pos += 1
                    continue

                m = RE_NEWLINE.search(source, pos)  # pyright: ignore[reportUnknownMemberType]
                stop = m.start() if m else length
                tokens.append((TOKEN_COMMENT_TEXT, pos, stop))
                pos = stop
            else:
                tokens.append((TOKEN_UNKNOWN, pos, pos + 1))
                pos += 1
        elif ch == "'":
            char_literal = _scan(RE_CHAR, source, pos)
            if char_literal is None:
                tokens.append((TOKEN_UNKNOWN, pos, pos + 1))
                pos += 1
            elif char_literal.startswith("'\\"):
                tokens.append((TOKEN_ESC_CHAR, pos, pos + len(char_literal)))
                pos += len(char_literal)
            else:
                tokens.append((TOKEN_CHAR, pos, pos + len(char_literal)))
                pos += len(char_literal)
        elif ch == '"':
            token, pos = _scan_string_literal(source, pos + 1)
            tokens.append(token)
        elif _is_name_first_ch(ord(ch)):
            word = _scan(RE_IDENTIFIER, source, pos)
            if word == "_":
                tokens.append((TOKEN_UNDERSCORE, pos, pos + 1))
                pos += 1
            elif word == "DROP":
                tokens.append((TOKEN_DROP, pos, pos + 4))
                pos += 4
            elif word == "PEEK_ALL":
                tokens.append((TOKEN_PEEK_ALL, pos, pos + 8))
                pos += 8
            elif word == "PEEK":
                tokens.append((TOKEN_PEEK, pos, pos + 4))
                pos += 4
            elif word == "POP_ALL":
                tokens.append((TOKEN_POP_ALL, pos, pos + 7))
                pos += 7
            elif word == "POP":
                tokens.append((TOKEN_POP, pos, pos + 3))
                pos += 3
            elif word == "PUSH_LITERAL":
                tokens.append((TOKEN_PUSH_LITERAL, pos, pos + 12))
                pos += 12
            elif word == "PUSH":
                tokens.append((TOKEN_PUSH, pos, pos + 4))
                pos += 4
            elif word == "SOI":
                tokens.append((TOKEN_SOI, pos, pos + 3))
                pos += 3
            elif word == "EOI":
                tokens.append((TOKEN_EOI, pos, pos + 3))
                pos += 3
            elif word == "ANY":
                tokens.append((TOKEN_ANY, pos, pos + 3))
                pos += 3
            elif word is None:
                tokens.append((TOKEN_UNKNOWN, pos, pos + 1))
                pos += 1
            else:
                tokens.append((TOKEN_IDENTIFIER, pos, pos + len(word)))
                pos += len(word)
        elif _is_number_ch(ord(ch)):
            if match := _scan(RE_INTEGER, source, pos):
                tokens.append((TOKEN_INTEGER, pos, pos + len(match)))
                pos += len(match)
            else:
                tokens.append((TOKEN_UNKNOWN, pos, pos + 1))
                pos += 1
        else:
            tokens.append((TOKEN_UNKNOWN, pos, pos + 1))
            pos += 1

    return tokens


def _skip_trivia(source: str, pos: int) -> int:
    m = RE_TRIVIA.match(source, pos)  # pyright: ignore[reportUnknownMemberType]
    return m.end() if m else pos


def _scan(pattern: re.Pattern[str], source: str, pos: int) -> str | None:
    m = pattern.match(source, pos)  # pyright: ignore[reportUnknownMemberType]
    return m.group() if m else None


def _scan_string_literal(source: str, pos: int) -> tuple[Token, int]:
    start = pos
    length = len(source)
    kind: TokenKind = TOKEN_STRING

    while pos < length:
        ch = source[pos]

        if ch == '"':
            # Token excludes opening and closing quotes.
            return ((kind, start, pos), pos + 1)

        if ch == "\\":
            pos += 2
            kind = TOKEN_STRING_ESC
        else:
            pos += 1

    return (TOKEN_UNKNOWN, start, length), length


def _is_name_first_ch(ch: int) -> bool:
    return (ch >= 65 and ch <= 90) or (ch >= 97 and ch <= 122) or ch == 95


def _is_number_ch(ch: int) -> bool:
    return ch == 45 or (ch >= 48 and ch <= 57)
