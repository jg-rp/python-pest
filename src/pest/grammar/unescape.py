import re

from .exceptions import PestGrammarSyntaxError
from .tokens import Token

_RE_ESCAPE = re.compile(r"(\\u\{[0-9a-fA-F]{2,6}\}|\\x[0-9a-fA-F]{2}|\\.)")


def unescape_string(escaped: str, token: Token, quote: str = '"') -> str:
    unescaped: list[str] = []
    parts = [p for p in _RE_ESCAPE.split(escaped) if p]
    length = len(parts)
    pos = 0

    while pos < length:
        part = parts[pos]
        pos += 1

        if not part.startswith("\\"):
            unescaped.append(part)
        elif part.endswith(quote):
            unescaped.append(quote)
        elif part == "\\\\":
            unescaped.append("\\")
        elif part == "\\/":
            unescaped.append("/")
        elif part == "\\b":
            unescaped.append("\b")
        elif part == "\\f":
            unescaped.append("\f")
        elif part == "\\n":
            unescaped.append("\n")
        elif part == "\\r":
            unescaped.append("\r")
        elif part == "\\t":
            unescaped.append("\t")
        elif part in ("\\u", "\\x"):
            # No digits
            raise PestGrammarSyntaxError(
                "invalid escape sequence",
                token=token,
            )
        elif part.startswith("\\u"):
            code_point = int(part[3:-1], 16)
            unescaped.append(chr(code_point))
        elif part.startswith("\\x"):
            code_point = int(part[2:], 16)
            unescaped.append(chr(code_point))
        else:
            raise PestGrammarSyntaxError(
                "invalid escape sequence",
                token=token,
            )

    return "".join(unescaped)
