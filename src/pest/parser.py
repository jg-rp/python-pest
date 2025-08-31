"""pest grammar parser."""

from .exceptions import PestGrammarSyntaxError
from .expression import Expression
from .expressions import CaseInsensitiveString
from .expressions import Choice
from .expressions import Identifier
from .expressions import NegativePredicate
from .expressions import Optional
from .expressions import PeekSlice
from .expressions import PositivePredicate
from .expressions import Push
from .expressions import PushLiteral
from .expressions import Range
from .expressions import Repeat
from .expressions import RepeatExact
from .expressions import RepeatMax
from .expressions import RepeatMin
from .expressions import RepeatOnce
from .expressions import RepeatRange
from .expressions import Rule
from .expressions import Sequence
from .expressions import String
from .grammar import Grammar
from .tokens import Token
from .tokens import TokenKind

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

POSTFIX_OPERATORS = frozenset(
    [
        TokenKind.OPTION_OP,
        TokenKind.REPEAT_OP,
        TokenKind.REPEAT_ONCE_OP,
        TokenKind.RBRACE,
    ]
)


class Parser:
    """pest grammar parser."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
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

    def parse(self) -> Grammar:
        grammar_doc: list[Token] = []
        while self.peek().kind == TokenKind.GRAMMAR_DOC:
            grammar_doc.append(self.next())

        rules = self.parse_rules()
        return Grammar(rules, grammar_doc)

    def parse_rules(self) -> dict[str, Rule]:
        rules: dict[str, Rule] = {}

        while True:
            if self.peek().kind == TokenKind.EOI:
                break

            rule_doc: list[Token] = []
            while self.peek().kind == TokenKind.RULE_DOC:
                rule_doc.append(self.next())

            identifier = self.eat(TokenKind.IDENTIFIER)
            self.eat(TokenKind.ASSIGN_OP)
            modifier = self.parse_modifier()
            self.eat(TokenKind.LBRACE)
            expression = self.parse_expression()
            self.eat(TokenKind.RBRACE)
            rules[identifier.value] = Rule(identifier, expression, modifier, rule_doc)

        return rules

    def parse_modifier(self) -> Token | None:
        if self.peek().kind == TokenKind.MODIFIER:
            return self.next()
        return None

    def parse_expression(self, precedence: int = PRECEDENCE_LOWEST) -> Expression:
        if self.peek().kind == TokenKind.CHOICE_OP:
            self.next()  # Ignore leading choice operator.

        if self.peek().kind == TokenKind.TAG:
            tag: Token | None = self.next()
            self.eat(TokenKind.ASSIGN_OP)
        else:
            tag = None

        token = self.current()
        left_kind = token.kind

        left: Expression

        if left_kind == TokenKind.STRING:
            left = String(self.next(), tag=tag)
        elif left_kind == TokenKind.LPAREN:
            left = self.parse_group()
        elif left_kind == TokenKind.IDENTIFIER:
            left = Identifier(self.next(), tag=tag)
        # TODO: other terminals
        elif left_kind == TokenKind.POSITIVE_PREDICATE:
            self.pos += 1
            left = PositivePredicate(self.parse_expression(PRECEDENCE_PREFIX), tag=tag)
        elif left_kind == TokenKind.NEGATIVE_PREDICATE:
            self.pos += 1
            left = NegativePredicate(self.parse_expression(PRECEDENCE_PREFIX), tag=tag)

        while True:
            kind = self.current().kind

            if (
                kind == TokenKind.EOI
                or PRECEDENCES.get(kind, PRECEDENCE_LOWEST) < precedence
                or kind not in INFIX_OPERATORS
            ):
                break

            left = self.parse_infix_expression(left)

        if self.current().kind in POSTFIX_OPERATORS:
            left = self.parse_postfix_expression(left)

        return left

    def parse_infix_expression(self, left: Expression) -> Expression:
        token = self.next()
        kind = token.kind
        precedence = PRECEDENCES.get(kind, PRECEDENCE_LOWEST)
        right = self.parse_expression(precedence)

        if kind == TokenKind.CHOICE_OP:
            return Choice(left, right)

        if kind == TokenKind.SEQUENCE_OP:
            return Sequence(left, right)

        raise PestGrammarSyntaxError(f"unexpected operator {kind}", token=token)

    def parse_postfix_expression(self, left: Expression) -> Expression:
        token = self.next()
        kind = token.kind

        # TODO:
