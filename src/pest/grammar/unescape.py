r"""Replace `\u{XX}` or `\u{XXXX}` escape sequences with Unicode code points."""

from .exceptions import PestGrammarSyntaxError
from .tokens import Token


def unescape_string(value: str, token: Token, quote: str = '"') -> str:
    """Return `value` with escape sequences replaced with Unicode code points."""
    unescaped: list[str] = []
    index = 0

    while index < len(value):
        ch = value[index]
        if ch == "\\":
            index += 1
            _ch, index = _decode_escape_sequence(value, index, token, quote)
            unescaped.append(_ch)
        else:
            unescaped.append(ch)
        index += 1
    return "".join(unescaped)


def _decode_escape_sequence(  # noqa: PLR0911
    value: str, index: int, token: Token, quote: str
) -> tuple[str, int]:
    try:
        ch = value[index]
    except IndexError as err:
        raise PestGrammarSyntaxError("incomplete escape sequence", token=token) from err

    # TODO: match these to Rust?
    if ch == quote:
        return quote, index
    if ch == "\\":
        return "\\", index
    if ch == "/":
        return "/", index
    if ch == "b":
        return "\x08", index
    if ch == "f":
        return "\x0c", index
    if ch == "n":
        return "\n", index
    if ch == "r":
        return "\r", index
    if ch == "t":
        return "\t", index
    if ch == "x":
        # TODO: handle incomplete \x escape sequence
        return chr(int(value[index + 1 : index + 3], 16)), index + 3
    if ch == "u":
        codepoint, index = _decode_hex_char(value, index, token)
        return chr(codepoint), index

    raise PestGrammarSyntaxError(
        f"unknown escape sequence at index {token.start + index - 1}",
        token=token,
    )


def _decode_hex_char(value: str, index: int, token: Token) -> tuple[int, int]:
    # TODO: use a regular expression?
    index += 1  # move past 'u'

    if value[index] != "{":
        raise PestGrammarSyntaxError(
            f"expected an opening brace, found {value[index]}",
            token=token,
        )

    index += 1  # move past '{'
    closing_brace_index = value.find("}", index)

    if closing_brace_index == -1:
        raise PestGrammarSyntaxError("unclosed Unicode escape sequence", token=token)

    hex_digit_length = closing_brace_index - index
    if hex_digit_length not in (2, 4, 6):
        raise PestGrammarSyntaxError(
            "expected \\u{00}, \\u{0000} or \\u{000000}", token=token
        )

    codepoint = _parse_hex_digits(value[index : index + hex_digit_length], token)
    index += hex_digit_length
    index += 1  # move past '}'
    return codepoint, index


def _parse_hex_digits(digits: str, token: Token) -> int:
    codepoint = 0
    for digit in digits.encode():
        codepoint <<= 4
        if digit >= 48 and digit <= 57:
            codepoint |= digit - 48
        elif digit >= 65 and digit <= 70:
            codepoint |= digit - 65 + 10
        elif digit >= 97 and digit <= 102:
            codepoint |= digit - 97 + 10
        else:
            raise PestGrammarSyntaxError(
                "invalid \\u{XXXX} escape sequence",
                token=token,
            )
    return codepoint
