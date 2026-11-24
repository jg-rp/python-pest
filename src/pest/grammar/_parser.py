from typing import Mapping

from . import _ast
from ._lexer import tokenize
from ._tokens import *
from ._tokens import Token, token_value
from .exceptions import PestGrammarSyntaxError


class Parser:
    __slots_ = (
        "builtin",
        "eoi",
        "length",
        "pos",
        "source",
        "tokens",
    )

    def __init__(
        self, source: str, tokens: list[Token], builtins: Mapping[str, _ast.Rule]
    ):
        self.source = source
        self.tokens = tokens
        self.builtins = builtins
        self.pos = 0
        self.length = len(tokens)
        self.eoi: Token = (TOKEN_EOI, self.length, self.length)

    @classmethod
    def parse(
        cls, source: str, builtins: Mapping[str, _ast.Rule]
    ) -> tuple[dict[str, _ast.Rule], list[str]]:
        return cls(source, tokenize(source), builtins).parse_grammar()

    def parse_grammar(self) -> tuple[dict[str, _ast.Rule], list[str]]:
        """"""
        # TODO:
        raise NotImplementedError(":(")

    def current(self) -> Token:
        """Return the current token without advancing the pointer."""
        if self.pos < self.length:
            return self.tokens[self.pos]
        return self.eoi

    def kind(self) -> int:
        """Return the kind of the current token without advancing the pointer."""
        if self.pos < self.length:
            return self.tokens[self.pos][0]
        return TOKEN_EOI

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
        return TOKEN_EOI

    def eat(self, kind: int, message: str | None = None) -> Token:
        token = self.current()
        if token[0] != kind:
            raise PestGrammarSyntaxError(
                message or f"unexpected {token_value(token, self.source)!r}",
                token,
                self.source,
            )

        self.pos += 1
        return token
