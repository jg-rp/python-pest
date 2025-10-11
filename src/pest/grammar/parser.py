"""pest grammar parser."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import PestGrammarSyntaxError
from .expressions import Choice
from .expressions import CIString
from .expressions import Drop
from .expressions import Group
from .expressions import Identifier
from .expressions import NegativePredicate
from .expressions import Optional
from .expressions import Peek
from .expressions import PeekAll
from .expressions import PeekSlice
from .expressions import Pop
from .expressions import PopAll
from .expressions import PositivePredicate
from .expressions import Push
from .expressions import PushLiteral
from .expressions import Range
from .expressions import Repeat
from .expressions import RepeatExact
from .expressions import RepeatMax
from .expressions import RepeatMin
from .expressions import RepeatMinMax
from .expressions import RepeatOnce
from .expressions import Sequence
from .expressions import String
from .rule import MODIFIER_MAP
from .rule import GrammarRule
from .rule import Rule
from .tokens import Token
from .tokens import TokenKind
from .unescape import unescape_string

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .expression import Expression


PRECEDENCE_LOWEST = 1
PRECEDENCE_CHOICE = 2
PRECEDENCE_SEQUENCE = 3
PRECEDENCE_PREFIX = 4

PRECEDENCES: dict[TokenKind, int] = {
    TokenKind.CHOICE_OP: PRECEDENCE_CHOICE,
    TokenKind.SEQUENCE_OP: PRECEDENCE_SEQUENCE,
}

INFIX_OPERATORS = frozenset(
    [
        TokenKind.CHOICE_OP,
        TokenKind.SEQUENCE_OP,
    ]
)


class Parser:
    """pest grammar parser."""

    def __init__(self, tokens: list[Token], builtins: Mapping[str, Rule]):
        self.tokens = tokens
        self.builtins = builtins
        self.pos = 0
        assert tokens
        self.eof = Token(TokenKind.EOI, "", -1, tokens[-1].grammar)

    def current(self) -> Token:
        try:
            return self.tokens[self.pos]
        except IndexError:
            return self.eof

    def next(self) -> Token:
        try:
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        except IndexError:
            return self.eof

    def peek(self, offset: int = 1) -> Token:
        try:
            return self.tokens[self.pos + offset]
        except IndexError:
            return self.eof

    def eat(self, kind: TokenKind, message: str | None = None) -> Token:
        token = self.next()
        if token.kind != kind:
            raise PestGrammarSyntaxError(
                message or f"unexpected {token.value!r}", token=token
            )
        return token

    def parse(self) -> tuple[dict[str, GrammarRule], list[str]]:
        grammar_doc: list[str] = []
        while self.current().kind == TokenKind.GRAMMAR_DOC:
            self.pos += 1
            grammar_doc.append(self.eat(TokenKind.COMMENT_TEXT).value)

        return self.parse_rules(), grammar_doc

    def parse_rules(self) -> dict[str, GrammarRule]:
        rules: dict[str, GrammarRule] = {}

        while True:
            if self.current().kind == TokenKind.EOI:
                break

            rule_doc: list[str] = []
            while self.current().kind == TokenKind.RULE_DOC:
                self.pos += 1
                rule_doc.append(self.eat(TokenKind.COMMENT_TEXT).value)

            identifier = self.eat(TokenKind.IDENTIFIER)
            self.eat(TokenKind.ASSIGN_OP)
            modifier = self.parse_modifier()
            self.eat(TokenKind.LBRACE)
            expression = self.parse_expression()
            self.eat(TokenKind.RBRACE)

            # TODO: validate rules
            # - duplicate rules

            rules[identifier.value] = GrammarRule(
                identifier.value, expression, modifier, rule_doc
            )

        return rules

    def parse_modifier(self) -> int:
        if self.current().kind == TokenKind.MODIFIER:
            return MODIFIER_MAP.get(self.next().value, 0)
        return 0

    def parse_expression(self, precedence: int = PRECEDENCE_LOWEST) -> Expression:  # noqa: PLR0912, PLR0915
        if self.current().kind == TokenKind.CHOICE_OP:
            self.next()  # Ignore leading choice operator.

        if self.current().kind == TokenKind.TAG:
            tag: str | None = self.next().value[1:]
            self.eat(TokenKind.ASSIGN_OP)
        else:
            tag = None

        token = self.current()
        left_kind = token.kind

        left: Expression

        if left_kind == TokenKind.STRING:
            left = String(self.next().value)
        elif left_kind == TokenKind.STRING_CI:
            left = CIString(self.next().value)
        elif left_kind == TokenKind.LPAREN:
            self.pos += 1
            left = Group(self.parse_expression(), tag=tag)
            self.eat(TokenKind.RPAREN)
        elif left_kind == TokenKind.IDENTIFIER:
            name = self.next().value
            if name != "EOI" and name in self.builtins:
                left = self.builtins[name]
            else:
                left = Identifier(name, tag=tag)
        elif left_kind == TokenKind.PUSH_LITERAL:
            self.pos += 1
            self.eat(TokenKind.LPAREN)
            left = PushLiteral(self.eat(TokenKind.STRING).value, tag=tag)
            self.eat(TokenKind.RPAREN)
        elif left_kind == TokenKind.PUSH:
            self.pos += 1
            self.eat(TokenKind.LPAREN)
            left = Push(self.parse_expression(), tag=tag)
            self.eat(TokenKind.RPAREN)
        elif left_kind == TokenKind.PEEK:
            self.pos += 1
            left = self.parse_peek_expression(tag)
        elif left_kind == TokenKind.PEEK_ALL:
            self.pos += 1
            left = PeekAll(tag=tag)
        elif left_kind == TokenKind.POP:
            self.pos += 1
            left = Pop(tag=tag)
        elif left_kind == TokenKind.DROP:
            self.pos += 1
            left = Drop(tag=tag)
        elif left_kind == TokenKind.POP_ALL:
            self.pos += 1
            left = PopAll(tag=tag)
        elif left_kind == TokenKind.CHAR:
            start = unescape_string(
                self.eat(TokenKind.CHAR).value[1:-1], token, quote="'"
            )
            self.eat(TokenKind.RANGE_OP)
            stop_token = self.eat(TokenKind.CHAR)
            left = Range(
                start,
                unescape_string(stop_token.value[1:-1], token, quote="'"),
                tag=tag,
            )
        elif left_kind == TokenKind.POSITIVE_PREDICATE:
            self.pos += 1
            left = PositivePredicate(self.parse_expression(PRECEDENCE_PREFIX), tag=tag)
        elif left_kind == TokenKind.NEGATIVE_PREDICATE:
            self.pos += 1
            left = NegativePredicate(self.parse_expression(PRECEDENCE_PREFIX), tag=tag)
        else:
            raise PestGrammarSyntaxError(f"unexpected token {token.kind}", token=token)

        left = self.parse_postfix_expression(left)

        while True:
            kind = self.current().kind

            if (
                kind == TokenKind.EOI
                or PRECEDENCES.get(kind, PRECEDENCE_LOWEST) < precedence
                or kind not in INFIX_OPERATORS
            ):
                break

            left = self.parse_infix_expression(left)

        return left

    def parse_infix_expression(self, left: Expression) -> Expression:
        token = self.next()
        kind = token.kind
        precedence = PRECEDENCES.get(kind, PRECEDENCE_LOWEST)
        right = self.parse_expression(precedence)

        if kind == TokenKind.CHOICE_OP:
            if isinstance(right, Choice):
                return Choice(left, *right.expressions)
            return Choice(left, right)

        if kind == TokenKind.SEQUENCE_OP:
            if isinstance(right, Sequence):
                return Sequence(left, *right.expressions)
            return Sequence(left, right)

        raise PestGrammarSyntaxError(f"unexpected operator {kind}", token=token)

    def parse_postfix_expression(self, expr: Expression) -> Expression:
        token = self.current()
        kind = token.kind

        if kind == TokenKind.OPTION_OP:
            self.pos += 1
            return Optional(expr)

        if kind == TokenKind.REPEAT_OP:
            self.pos += 1
            return Repeat(expr)

        if kind == TokenKind.REPEAT_ONCE_OP:
            self.pos += 1
            return RepeatOnce(expr)

        if kind == TokenKind.LBRACE:
            self.pos += 1
            return self.parse_repeat_expression(expr)

        return expr

    def parse_repeat_expression(self, expr: Expression) -> Expression:
        token = self.next()
        kind = token.kind

        if kind == TokenKind.NUMBER:
            number = token
            if self.current().kind == TokenKind.RBRACE:
                self.pos += 1
                return RepeatExact(expr, int(number.value))

            self.eat(TokenKind.COMMA)

            if self.current().kind == TokenKind.RBRACE:
                self.pos += 1
                return RepeatMin(expr, int(number.value))

            stop = self.eat(TokenKind.NUMBER)
            self.eat(TokenKind.RBRACE)
            return RepeatMinMax(expr, int(number.value), int(stop.value))

        if kind == TokenKind.COMMA:
            number = self.eat(TokenKind.NUMBER)
            self.eat(TokenKind.RBRACE)
            return RepeatMax(expr, int(number.value))

        raise PestGrammarSyntaxError("expected a number or a comma", token=token)

    def parse_peek_expression(self, tag: str | None) -> Expression:
        if self.current().kind != TokenKind.LBRACKET:
            return Peek(tag=tag)

        self.eat(TokenKind.LBRACKET)
        if self.current().kind == TokenKind.INTEGER:
            start: str | None = self.next().value
        else:
            start = None

        self.eat(TokenKind.RANGE_OP)

        if self.current().kind == TokenKind.INTEGER:
            stop: str | None = self.next().value
        else:
            stop = None

        self.eat(TokenKind.RBRACKET)
        return PeekSlice(start, stop, tag=tag)
