import re
from typing import Literal

from . import _ast
from ._lexer import tokenize
from ._modifiers import MODIFIER_MAP
from ._tokens import *
from ._tokens import TOKEN_NAMES, Token, TokenKind, span, token_value
from .exceptions import PestGrammarSyntaxError

PRECEDENCE_LOWEST: Literal[1] = 1
PRECEDENCE_CHOICE: Literal[2] = 2
PRECEDENCE_SEQUENCE: Literal[3] = 3
PRECEDENCE_PREFIX: Literal[4] = 4

type Precedence = Literal[1, 2, 3, 4]

PRECEDENCES: dict[TokenKind, Precedence] = {
    TOKEN_PIPE: PRECEDENCE_CHOICE,
    TOKEN_TILDE: PRECEDENCE_SEQUENCE,
}

_RE_ESCAPE = re.compile(r"(\\u\{[0-9a-fA-F]{2,6}\}|\\x[0-9a-fA-F]{2}|\\.)")


class Grammar:
    """Parse a pest grammar."""

    __slots__ = (
        "eoi",
        "length",
        "pos",
        "source",
        "tokens",
    )

    def __init__(self, source: str, tokens: list[Token]):
        self.source = source
        self.tokens = tokens
        self.pos = 0
        self.length = len(tokens)
        self.eoi: Token = (TOKEN_EOF, self.length, self.length)

    @classmethod
    def parse(cls, source: str) -> tuple[dict[str, _ast.Rule], list[str]]:
        return cls(source, tokenize(source)).parse_grammar()

    def parse_grammar(self) -> tuple[dict[str, _ast.Rule], list[str]]:
        """Return parsed rules and grammar doc lines."""
        grammar_doc: list[str] = []

        while self.kind() == TOKEN_GRAMMAR_DOC:
            self.pos += 1
            grammar_doc.append(token_value(self.eat(TOKEN_COMMENT_TEXT), self.source))

        rules: dict[str, _ast.Rule] = {}

        while self.kind() != TOKEN_EOF:
            rule_doc: list[str] = []

            while self.kind() == TOKEN_RULE_DOC:
                self.pos += 1
                rule_doc.append(token_value(self.eat(TOKEN_COMMENT_TEXT), self.source))

            rule_name_token = self.eat(TOKEN_IDENTIFIER)
            rule_name = token_value(rule_name_token, self.source)
            self.eat(TOKEN_ASSIGN)

            rule_modifier = MODIFIER_MAP.get(self.kind(), 0)
            if rule_modifier > 0:
                self.pos += 1

            self.eat(TOKEN_LBRACE)
            expression = self.parse_expression()
            self.eat(TOKEN_RBRACE)

            rules[rule_name] = (
                _ast.RULE,
                rule_name_token,
                rule_name,
                expression,
                rule_modifier,
                tuple(rule_doc),
            )

        return rules, grammar_doc

    def parse_expression(
        self, *, precedence: Precedence = PRECEDENCE_LOWEST
    ) -> _ast.Expression:
        if self.kind() == TOKEN_PIPE:
            # Ignore leading choice operator.
            self.pos += 1

        tag: str | None = None

        if self.kind() == TOKEN_HASH:
            self.pos += 1
            tag_token = self.eat(TOKEN_IDENTIFIER)
            self.eat(TOKEN_ASSIGN, message="expected '=' after tag name")
            tag = token_value(tag_token, self.source)

        left = self.parse_postfix_expression(self.parse_primary(tag))

        while True:
            kind = self.kind()

            if (
                kind not in (TOKEN_PIPE, TOKEN_TILDE)
                or PRECEDENCES.get(kind, PRECEDENCE_LOWEST) < precedence
            ):
                return left

            left = self.parse_infix_expression(left, kind)

    def parse_primary(self, tag: str | None) -> _ast.Expression:
        kind = self.kind()

        if kind == TOKEN_STRING:
            token = self.next()
            return (_ast.STRING, token, token_value(token, self.source))

        if kind == TOKEN_STRING_ESC:
            token = self.next()
            return (
                _ast.STRING,
                token,
                self.unescape_string(
                    token_value(token, self.source),
                    token,
                    '"',
                ),
            )

        if kind == TOKEN_CARET:
            self.pos += 1
            kind = self.kind()

            if kind == TOKEN_STRING:
                token = self.next()
                return (_ast.CI_STRING, token, token_value(token, self.source))

            if kind == TOKEN_STRING_ESC:
                token = self.next()
                return (
                    _ast.CI_STRING,
                    token,
                    self.unescape_string(
                        token_value(token, self.source),
                        token,
                        '"',
                    ),
                )

            raise PestGrammarSyntaxError(
                "expected a string literal after '^'",
                token=self.current(),
                source=self.source,
            )

        if kind in (TOKEN_CHAR, TOKEN_ESC_CHAR):
            token = self.next()
            start_ch = self.unescape_char(token)
            self.eat(TOKEN_DOUBLE_DOT)
            stop_ch = self.unescape_char(self.next())
            return (_ast.RANGE, token, tag, start_ch, stop_ch)

        if kind == TOKEN_AMP:
            return (
                _ast.POSITIVE_PREDICATE,
                self.next(),
                tag,
                self.parse_expression(precedence=PRECEDENCE_PREFIX),
            )

        if kind == TOKEN_EXCLAIM:
            return (
                _ast.NEGATIVE_PREDICATE,
                self.next(),
                tag,
                self.parse_expression(precedence=PRECEDENCE_PREFIX),
            )

        if kind == TOKEN_LPAREN:
            token = self.next()
            expr = self.parse_expression()
            self.eat(TOKEN_RPAREN, message="unbalanced brackets")
            return (_ast.GROUP, token, tag, expr)

        if kind == TOKEN_IDENTIFIER:
            token = self.next()
            rule_name = token_value(token, self.source)
            return _ast.IDENT, token, tag, rule_name

        if kind == TOKEN_PUSH_LITERAL:
            token = self.next()
            self.eat(TOKEN_LPAREN)
            # TODO: TOKEN_STRING_ESC
            value = token_value(self.eat(TOKEN_STRING), self.source)
            expr = (_ast.PUSH_LITERAL, token, tag, value)
            self.eat(TOKEN_RPAREN)
            return expr

        if kind == TOKEN_PUSH:
            token = self.next()
            self.eat(TOKEN_LPAREN)
            expr = self.parse_expression()
            self.eat(TOKEN_RPAREN)
            return (_ast.PUSH, token, tag, expr)

        if kind == TOKEN_PEEK:
            token = self.next()

            if self.kind() == TOKEN_LBRACKET:
                self.pos += 1
                start: int | None = None
                stop: int | None = None

                if self.kind() == TOKEN_INTEGER:
                    start = int(token_value(self.next(), self.source))

                self.eat(TOKEN_DOUBLE_DOT)

                if self.kind() == TOKEN_INTEGER:
                    stop = int(token_value(self.next(), self.source))

                self.eat(TOKEN_RBRACKET)
                # TODO: reject negative integers?
                return (_ast.PEEK_SLICE, token, tag, start, stop)

            return (_ast.PEEK, token, tag)

        if kind == TOKEN_PEEK_ALL:
            return (_ast.PEEK_ALL, self.next(), tag)

        if kind == TOKEN_POP:
            return (_ast.POP, self.next(), tag)

        if kind == TOKEN_POP_ALL:
            return (_ast.POP_ALL, self.next(), tag)

        if kind == TOKEN_DROP:
            return (_ast.DROP, self.next(), tag)

        if kind == TOKEN_ANY:
            return (_ast.ANY, self.next(), tag)

        if kind == TOKEN_SOI:
            return (_ast.SOI, self.next(), tag)

        if kind == TOKEN_EOI:
            token = self.next()
            return (_ast.RULE, token, "EOI", (_ast.EOI, token, tag), 0, ())

        raise PestGrammarSyntaxError(
            f"unexpected token {TOKEN_NAMES[self.kind()]} "
            f"({token_value(self.current(), self.source)})",
            token=self.current(),
            source=self.source,
        )

    def parse_infix_expression(
        self, left: _ast.Expression, kind: TokenKind
    ) -> _ast.Expression:
        op_token = self.next()
        prec = PRECEDENCES.get(kind, PRECEDENCE_LOWEST)
        right = self.parse_expression(precedence=prec)
        span_ = span(left[1], right[1])

        if kind == TOKEN_PIPE:
            return (_ast.CHOICE, span_, left, right)

        if kind == TOKEN_TILDE:
            return (_ast.SEQUENCE, span_, left, right)

        raise PestGrammarSyntaxError(
            f"unknown infix operator ({token_value(op_token, self.source)})",
            token=op_token,
            source=self.source,
        )

    def parse_postfix_expression(self, expr: _ast.Expression) -> _ast.Expression:
        kind = self.kind()

        if kind == TOKEN_QUESTION:
            token = self.next()
            return (_ast.OPTIONAL, token, expr)

        if kind == TOKEN_ASTERISK:
            token = self.next()
            return (_ast.REPEAT, token, expr)

        if kind == TOKEN_PLUS:
            token = self.next()
            return (_ast.REPEAT_ONCE, token, expr)

        if kind == TOKEN_LBRACE:
            token = self.next()
            kind = self.kind()

            min_: int | None = None
            max_: int | None = None

            if kind == TOKEN_INTEGER:
                token = self.next()
                min_ = int(token_value(token, self.source))
                if min_ < 0:
                    raise PestGrammarSyntaxError(
                        "repeat min must be greater or equal to zero",
                        token=token,
                        source=self.source,
                    )

                if self.kind() == TOKEN_RBRACE:
                    self.pos += 1
                    return (_ast.REPEAT_EXACT, token, expr, min_)

                self.eat(TOKEN_COMMA)

                if self.kind() == TOKEN_RBRACE:
                    self.pos += 1
                    return (_ast.REPEAT_MIN, token, expr, min_)

                token = self.eat(TOKEN_INTEGER)
                max_ = int(token_value(token, self.source))
                if max_ < 0:
                    raise PestGrammarSyntaxError(
                        "repeat max must be greater or equal to zero",
                        token=token,
                        source=self.source,
                    )

                self.eat(TOKEN_RBRACE)
                return (_ast.REPEAT_MIN_MAX, token, expr, min_, max_)

            if kind == TOKEN_COMMA:
                self.pos += 1
                max_ = int(token_value(self.eat(TOKEN_INTEGER), self.source))
                self.eat(TOKEN_RBRACE)
                return (_ast.REPEAT_MAX, token, expr, max_)

            raise PestGrammarSyntaxError(
                "expected a number or comma "
                f"({token_value(self.current(), self.source)})",
                token=self.current(),
                source=self.source,
            )

        return expr

    def current(self) -> Token:
        """Return the current token without advancing the pointer."""
        if self.pos < self.length:
            return self.tokens[self.pos]
        return self.eoi

    def kind(self) -> TokenKind:
        """Return the kind of the current token without advancing the pointer."""
        if self.pos < self.length:
            return self.tokens[self.pos][0]
        return TOKEN_EOF

    def value(self) -> str:
        """Return the string value associated with the current token."""
        if self.pos < self.length:
            return token_value(self.tokens[self.pos], self.source)
        return ""

    def next(self) -> Token:
        """Return the current token and advance the pointer."""
        if self.pos < self.length:
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return self.eoi

    def peek(self, n: int = 1) -> Token:
        """Return the token a pos+n without advancing the pointer."""
        if self.pos + n < self.length:
            return self.tokens[self.pos + n]
        return self.eoi

    def peek_kind(self, n: int = 1) -> int:
        if self.pos + n < self.length:
            return self.tokens[self.pos + n][0]
        return TOKEN_EOF

    def eat(self, kind: TokenKind, message: str | None = None) -> Token:
        token = self.current()
        if token[0] != kind:
            raise PestGrammarSyntaxError(
                message
                or f"expected {TOKEN_NAMES[kind]}, found {token_value(token, self.source)!r}",
                token=token,
                source=self.source,
            )

        self.pos += 1
        return token

    def unescape_string(self, escaped: str, token: Token, quote: str) -> str:
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
                    source=self.source,
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
                    source=self.source,
                )

        return "".join(unescaped)

    def unescape_char(self, token: Token) -> str:
        if token[0] == TOKEN_CHAR:
            return token_value(token, self.source)[1:-1]

        return self.unescape_string(
            token_value(token, self.source)[1:-1],
            token,
            "'",
        )
