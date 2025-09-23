"""pest grammar lexical scanner."""

from __future__ import annotations

from typing import Callable
from typing import Never
from typing import Optional
from typing import TypeAlias

import regex as re

from .exceptions import PestGrammarSyntaxError
from .tokens import Token
from .tokens import TokenKind
from .unescape import unescape_string

StateFn: TypeAlias = Callable[[], Optional["StateFn"]]

RE_ASSIGN_OP = re.compile(r"=")  # TODO: scan until ch?
RE_DROP = re.compile(r"DROP")
RE_GRAMMAR_DOC = re.compile(r"//!")
RE_IDENTIFIER = re.compile(r"[_a-zA-Z][_a-zA-Z0-9]*")
RE_INTEGER = re.compile(r"-?[0-9]+")
RE_MODIFIER = re.compile(r"[_@\$!]")
RE_NEWLINE = re.compile(r"\r?\n")
RE_NUMBER = re.compile(r"[0-9]+")
RE_PEEK = re.compile(r"PEEK")
RE_PEEK_ALL = re.compile(r"PEEK_ALL")
RE_POP = re.compile(r"POP")
RE_POP_ALL = re.compile(r"POP_ALL")
RE_PUSH = re.compile(r"PUSH")
RE_PUSH_LITERAL = re.compile(r"PUSH_LITERAL")
RE_RANGE_OP = re.compile(r"..")
RE_RULE_DOC = re.compile(r"///")
RE_TAG = re.compile(r"#[_a-zA-z][_a-zA-Z0-9]+(?=\s*=)")
RE_WHITESPACE = re.compile(r"[ \t\n\r]+")
RE_CHAR = re.compile(
    r"'\\[\\\"\r\n\t\0']'|'\\x[0-9a-fA-F]{2}'|'\\u\{[0-9a-fA-F]{2,6}\}'|'.'"
)
RE_LINE_COMMENT = re.compile(r"//(?!/|!).*")
RE_BLOCK_COMMENT = re.compile(r"/\*(?:[^*/]|\*(?!/)|/(?!\*)|(?R))*\*/")

ESCAPES = frozenset(["n", "r", "t", "u", "x", "\\", '"', "0", "'"])


def tokenize(grammar: str) -> list[Token]:
    """Return tokens from scanning _grammar_."""
    return Scanner(grammar).tokens


class Scanner:
    """pest grammar lexical scanner."""

    __slots__ = ("tokens", "start", "pos", "grammar")

    def __init__(self, grammar: str) -> None:
        self.tokens: list[Token] = []
        self.start = 0
        self.pos = 0
        self.grammar = grammar

        state: StateFn | None = self.scan_grammar
        while state is not None:
            state = state()

    def emit(self, kind: TokenKind, value: str) -> None:
        self.tokens.append(Token(kind, value, self.start, self.grammar))
        self.start = self.pos

    def next(self) -> str:
        try:
            ch = self.grammar[self.pos]
            self.pos += 1
            return ch
        except IndexError:
            return ""

    def peek(self) -> str:
        try:
            return self.grammar[self.pos]
        except IndexError:
            return ""

    def scan(self, pattern: re.Pattern[str]) -> str | None:
        match = pattern.match(self.grammar, self.pos)
        if match:
            self.pos += match.end() - match.start()
            return match[0]
        return None

    def scan_until(self, pattern: re.Pattern[str]) -> str | None:
        match = pattern.search(self.grammar, self.pos)
        if match:
            self.pos = match.start()
            return self.grammar[self.start : match.start()]
        return None

    def skip(self, pattern: re.Pattern[str]) -> bool:
        match = pattern.match(self.grammar, self.pos)
        if match:
            self.pos += match.end() - match.start()
            self.start = self.pos
            return True
        return False

    def skip_trivia(self) -> None:
        """Skip whitespace and/or comments."""
        while True:
            if not any(
                (
                    self.skip(RE_WHITESPACE),
                    self.skip(RE_LINE_COMMENT),
                    self.skip(RE_BLOCK_COMMENT),
                )
            ):
                break

    def error(self, message: str) -> Never:
        token = Token(TokenKind.ERROR, self.grammar[self.pos], self.start, self.grammar)
        raise PestGrammarSyntaxError(message, token=token)

    def scan_grammar(self) -> StateFn | None:
        self.skip_trivia()

        if value := self.scan(RE_GRAMMAR_DOC):
            self.emit(TokenKind.GRAMMAR_DOC, value)
            return self.scan_grammar_doc_inner

        return self.scan_grammar_rule

    def scan_grammar_doc_inner(self) -> StateFn | None:
        if self.peek() in (" ", "\t"):
            self.next()

        if value := self.scan_until(RE_NEWLINE):
            self.emit(TokenKind.COMMENT_TEXT, value)
        else:
            # Empty comment text
            self.emit(TokenKind.COMMENT_TEXT, "")

        return self.scan_grammar

    def scan_grammar_rule(self) -> StateFn | None:  # noqa: PLR0911
        self.skip_trivia()

        if value := self.scan(RE_RULE_DOC):
            self.emit(TokenKind.RULE_DOC, value)
            return self.scan_rule_doc_inner

        self.skip_trivia()

        if value := self.scan(RE_IDENTIFIER):
            self.emit(TokenKind.IDENTIFIER, value)
        elif self.pos == len(self.grammar):
            return None
        else:
            return self.error("expected a rule")

        self.skip_trivia()

        if self.peek() == "=":
            self.emit(TokenKind.ASSIGN_OP, self.next())
        else:
            return self.error("expected the assignment operator")

        self.skip_trivia()

        if value := self.scan(RE_MODIFIER):
            self.emit(TokenKind.MODIFIER, value)
            self.skip_trivia()

        if self.peek() == "{":
            self.emit(TokenKind.LBRACE, self.next())
        else:
            return self.error("expected an opening brace")

        self.accept_expression()

        if self.peek() == "}":
            self.emit(TokenKind.RBRACE, self.next())
        else:
            return self.error("expected a closing brace")

        # TODO: or loop
        return self.scan_grammar_rule

    def scan_rule_doc_inner(self) -> StateFn | None:
        if self.peek() in (" ", "\t"):
            self.next()

        if value := self.scan_until(RE_NEWLINE):
            self.emit(TokenKind.COMMENT_TEXT, value)
        else:
            # Empty comment text
            self.emit(TokenKind.COMMENT_TEXT, "")

        return self.scan_grammar_rule

    def accept_expression(self) -> None:
        self.skip_trivia()

        if self.peek() == "|":
            self.emit(TokenKind.CHOICE_OP, self.next())
            self.skip_trivia()

        self.accept_term()

        while True:
            self.skip_trivia()
            if self.peek() == "~":
                self.emit(TokenKind.SEQUENCE_OP, self.next())
                self.skip_trivia()
                self.accept_term()
            elif self.peek() == "|":
                self.emit(TokenKind.CHOICE_OP, self.next())
                self.skip_trivia()
                self.accept_term()
            else:
                break

    def accept_term(self) -> None:
        if value := self.scan(RE_TAG):
            # Assumes RE_TAG is using a lookahead assertion for "=".
            self.emit(TokenKind.TAG, value)
            self.skip_trivia()
            self.emit(TokenKind.ASSIGN_OP, self.next())
            self.skip_trivia()

        if self.peek() == "&":
            self.emit(TokenKind.POSITIVE_PREDICATE, self.next())
            self.skip_trivia()
        elif self.peek() == "!":
            while self.peek() == "!":
                self.emit(TokenKind.NEGATIVE_PREDICATE, self.next())
                self.skip_trivia()

        if self.accept_terminal():
            self.accept_postfix_op()
            return

        if self.peek() == "(":
            self.emit(TokenKind.LPAREN, self.next())
        else:
            self.error("expected an opening paren")

        self.skip_trivia()
        self.accept_expression()
        self.skip_trivia()

        if self.peek() == ")":
            self.emit(TokenKind.RPAREN, self.next())
        else:
            self.error("expected a closing paren")

        self.accept_postfix_op()

    def accept_terminal(self) -> bool:  # noqa: PLR0911, PLR0912, PLR0915
        if value := self.scan(RE_PUSH_LITERAL):
            self.emit(TokenKind.PUSH_LITERAL, value)
            self.skip_trivia()

            if self.peek() == "(":
                self.emit(TokenKind.LPAREN, self.next())
            else:
                self.error("expected an opening paren")

            self.skip_trivia()
            self.accept_string()
            self.skip_trivia()

            if self.peek() == ")":
                self.emit(TokenKind.RPAREN, self.next())
            else:
                self.error("expected a closing paren")

            return True

        if value := self.scan(RE_PUSH):
            self.emit(TokenKind.PUSH, value)
            self.skip_trivia()

            if self.peek() == "(":
                self.emit(TokenKind.LPAREN, self.next())
            else:
                self.error("expected an opening paren")

            self.skip_trivia()
            self.accept_expression()
            self.skip_trivia()

            if self.peek() == ")":
                self.emit(TokenKind.RPAREN, self.next())
            else:
                self.error("expected a closing paren")

            return True

        if value := self.scan(RE_PEEK_ALL):
            self.emit(TokenKind.PEEK_ALL, value)
            return True

        if value := self.scan(RE_POP_ALL):
            self.emit(TokenKind.POP_ALL, value)
            return True

        if value := self.scan(RE_POP):
            self.emit(TokenKind.POP, value)
            return True

        if value := self.scan(RE_DROP):
            self.emit(TokenKind.DROP, value)
            return True

        if value := self.scan(RE_PEEK):
            self.emit(TokenKind.PEEK, value)
            if self.peek() == "[":
                self.emit(TokenKind.LBRACKET, self.next())
            else:
                return True

            self.skip_trivia()

            if value := self.scan(RE_INTEGER):
                self.emit(TokenKind.INTEGER, value)
                self.skip_trivia()

            if value := self.scan(RE_RANGE_OP):
                self.emit(TokenKind.RANGE_OP, value)
            else:
                self.error("expected a range operator")

            if value := self.scan(RE_INTEGER):
                self.emit(TokenKind.INTEGER, value)
                self.skip_trivia()

            if self.peek() == "]":
                self.emit(TokenKind.RBRACKET, self.next())
            else:
                self.error("expected a closing paren")

            return True

        if value := self.scan(RE_IDENTIFIER):
            self.emit(TokenKind.IDENTIFIER, value)
            return True

        if self.accept_string() or self.accept_ci_string():
            return True

        if value := self.scan(RE_CHAR):
            self.emit(TokenKind.CHAR, value)
            self.skip_trivia()

            if value := self.scan(RE_RANGE_OP):
                self.emit(TokenKind.RANGE_OP, value)
            else:
                self.error("expected a range operator")

            self.skip_trivia()

            if value := self.scan(RE_CHAR):
                self.emit(TokenKind.CHAR, value)
            else:
                self.error("expected a character")

            return True

        return False

    def accept_postfix_op(self) -> None:
        ch = self.peek()

        if ch == "?":
            self.emit(TokenKind.OPTION_OP, self.next())
        elif ch == "*":
            self.emit(TokenKind.REPEAT_OP, self.next())
        elif ch == "+":
            self.emit(TokenKind.REPEAT_ONCE_OP, self.next())
        elif ch == "{":
            self.emit(TokenKind.LBRACE, self.next())

            while True:
                self.skip_trivia()
                if self.peek() == ",":
                    self.emit(TokenKind.COMMA, self.next())
                elif value := self.scan(RE_NUMBER):
                    self.emit(TokenKind.NUMBER, value)
                else:
                    break

            self.skip_trivia()
            if self.peek() == "}":
                self.emit(TokenKind.RBRACE, self.next())
            else:
                self.error("expected a closing brace")

    def accept_string(self) -> bool:
        if self.peek() != '"':
            return False

        self.pos += 1  # Skip opening quote.
        self.start = self.pos
        needs_unescaping = False

        while True:
            c = self.next()

            if c == "\\":
                peeked = self.peek()
                if peeked in ESCAPES:
                    self.next()
                    needs_unescaping = True
                else:
                    self.error("invalid escape")

            if not c:
                self.error(f"unclosed string starting at index {self.start}")

            if c == '"':
                value = self.grammar[self.start : self.pos - 1]
                if needs_unescaping:
                    value = unescape_string(
                        value, Token(TokenKind.STRING, value, self.start, self.grammar)
                    )
                self.emit(TokenKind.STRING, value)
                return True

    def accept_ci_string(self) -> bool:
        if self.peek() != "^":
            return False

        # Skip '^'.
        self.pos += 1
        self.start = self.pos

        if self.peek() != '"':
            self.error("expected a string literal")

        # Skip opening quote.
        self.pos += 1
        self.start = self.pos
        needs_unescaping = False

        while True:
            c = self.next()

            if c == "\\":
                peeked = self.peek()
                if peeked in ESCAPES:
                    self.next()
                    needs_unescaping = True
                else:
                    self.error("invalid escape")

            if not c:
                self.error(f"unclosed string starting at index {self.start}")

            if c == '"':
                value = self.grammar[self.start : self.pos - 1]
                if needs_unescaping:
                    value = unescape_string(
                        value,
                        Token(TokenKind.STRING_CI, value, self.start, self.grammar),
                    )
                self.emit(TokenKind.STRING_CI, value)
                return True
