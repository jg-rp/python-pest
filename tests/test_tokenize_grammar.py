import dataclasses
import operator

import pytest

from pest.grammar import _lexer
from pest.grammar._tokens import *
from pest.grammar._tokens import token_value


@dataclasses.dataclass
class Case:
    name: str
    source: str
    want: list[tuple[int, str]]


def tokenize(source: str) -> list[tuple[int, str]]:
    ts = _lexer.tokenize(source)
    return [(t[0], token_value(t, source)) for t in ts]


CASES: list[Case] = [
    Case(
        "line comment",
        "// some comment",
        [],
    ),
    Case(
        "one line multi line comment",
        "/* 1-line multiline comment */",
        [],
    ),
    Case(
        "multi line comment",
        "/*\nmultiline comment\n*/",
        [],
    ),
    Case(
        "multi line comment with nested line comments",
        (
            "/*\n\t// Line comment inside multiline\n\n\t"
            "/*\n\t\t(Multiline inside) multiline\n\t"
            "*/\n\n\tInvalid segment of grammar below (repeated rule)\n\n\t"
            'WHITESPACE = _{ "hi" }\n'
            "*/"
        ),
        [],
    ),
    Case(
        "grammar doc",
        "//! some comment",
        [
            (TOKEN_GRAMMAR_DOC, "//!"),
            (TOKEN_COMMENT_TEXT, " some comment"),
        ],
    ),
    Case(
        "multi line grammar doc",
        "//! some comment\n//! another comment",
        [
            (TOKEN_GRAMMAR_DOC, "//!"),
            (TOKEN_COMMENT_TEXT, " some comment"),
            (TOKEN_GRAMMAR_DOC, "//!"),
            (TOKEN_COMMENT_TEXT, " another comment"),
        ],
    ),
    Case(
        "multi line grammar doc carriage return",
        "//! some comment\r\n//! another comment",
        [
            (TOKEN_GRAMMAR_DOC, "//!"),
            (TOKEN_COMMENT_TEXT, " some comment"),
            (TOKEN_GRAMMAR_DOC, "//!"),
            (TOKEN_COMMENT_TEXT, " another comment"),
        ],
    ),
    Case(
        "string",
        'string = { "abc" }',
        [
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_STRING, "abc"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "insensitive",
        'insensitive = { ^"abc" }',
        [
            (TOKEN_IDENTIFIER, "insensitive"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_CARET, "^"),
            (TOKEN_STRING, "abc"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "range",
        "range = { '0'..'9' }",
        [
            (TOKEN_IDENTIFIER, "range"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_CHAR, "'0'"),
            (TOKEN_DOUBLE_DOT, ".."),
            (TOKEN_CHAR, "'9'"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "ident",
        "ident = { string }",
        [
            (TOKEN_IDENTIFIER, "ident"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "pos pred",
        "pos_pred = { &string }",
        [
            (TOKEN_IDENTIFIER, "pos_pred"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_AMP, "&"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "neg pred",
        "neg_pred = { !string }",
        [
            (TOKEN_IDENTIFIER, "neg_pred"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_EXCLAIM, "!"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "double neg pred",
        "double_neg_pred = { !!string }",
        [
            (TOKEN_IDENTIFIER, "double_neg_pred"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_EXCLAIM, "!"),
            (TOKEN_EXCLAIM, "!"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "sequence",
        "sequence = !{ string ~ string }",
        [
            (TOKEN_IDENTIFIER, "sequence"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_EXCLAIM, "!"),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_TILDE, "~"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "sequence compound",
        "sequence_compound = ${ string ~ string }",
        [
            (TOKEN_IDENTIFIER, "sequence_compound"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_DOLLAR, "$"),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_TILDE, "~"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "sequence atomic",
        "sequence_atomic = @{ string ~ string }",
        [
            (TOKEN_IDENTIFIER, "sequence_atomic"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_AT, "@"),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_TILDE, "~"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "sequence silent",
        "sequence_silent = _{ string ~ string }",
        [
            (TOKEN_IDENTIFIER, "sequence_silent"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_UNDERSCORE, "_"),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_TILDE, "~"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "tag",
        "node_tag = { #string = string }",
        [
            (TOKEN_IDENTIFIER, "node_tag"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_HASH, "#"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "choice",
        "choice = { string | range }",
        [
            (TOKEN_IDENTIFIER, "choice"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_PIPE, "|"),
            (TOKEN_IDENTIFIER, "range"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "choice prefix",
        "choice = { | string | range }",
        [
            (TOKEN_IDENTIFIER, "choice"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_PIPE, "|"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_PIPE, "|"),
            (TOKEN_IDENTIFIER, "range"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "optional",
        "optional = { string? }",
        [
            (TOKEN_IDENTIFIER, "optional"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_QUESTION, "?"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "repeat",
        "repeat = { string* }",
        [
            (TOKEN_IDENTIFIER, "repeat"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_ASTERISK, "*"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "repeat once",
        "repeat_once = { string+ }",
        [
            (TOKEN_IDENTIFIER, "repeat_once"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_PLUS, "+"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "repeat min",
        "repeat_min = { string{2,} }",
        [
            (TOKEN_IDENTIFIER, "repeat_min"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_LBRACE, "{"),
            (TOKEN_INTEGER, "2"),
            (TOKEN_COMMA, ","),
            (TOKEN_RBRACE, "}"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "repeat max",
        "repeat_max = { string{,3} }",
        [
            (TOKEN_IDENTIFIER, "repeat_max"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_LBRACE, "{"),
            (TOKEN_COMMA, ","),
            (TOKEN_INTEGER, "3"),
            (TOKEN_RBRACE, "}"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "soi",
        "soi_at_start = { SOI ~ string }",
        [
            (TOKEN_IDENTIFIER, "soi_at_start"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_SOI, "SOI"),
            (TOKEN_TILDE, "~"),
            (TOKEN_IDENTIFIER, "string"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
    Case(
        "push and pop",
        """repeat_mutate_stack = { (PUSH('a'..'c') ~ ",")* ~ POP ~ POP ~ POP }""",
        [
            (TOKEN_IDENTIFIER, "repeat_mutate_stack"),
            (TOKEN_ASSIGN, "="),
            (TOKEN_LBRACE, "{"),
            (TOKEN_LPAREN, "("),
            (TOKEN_PUSH, "PUSH"),
            (TOKEN_LPAREN, "("),
            (TOKEN_CHAR, "'a'"),
            (TOKEN_DOUBLE_DOT, ".."),
            (TOKEN_CHAR, "'c'"),
            (TOKEN_RPAREN, ")"),
            (TOKEN_TILDE, "~"),
            (TOKEN_STRING, ","),
            (TOKEN_RPAREN, ")"),
            (TOKEN_ASTERISK, "*"),
            (TOKEN_TILDE, "~"),
            (TOKEN_POP, "POP"),
            (TOKEN_TILDE, "~"),
            (TOKEN_POP, "POP"),
            (TOKEN_TILDE, "~"),
            (TOKEN_POP, "POP"),
            (TOKEN_RBRACE, "}"),
        ],
    ),
]


@pytest.mark.parametrize("case", CASES, ids=operator.attrgetter("name"))
def test_tokenizer(case: Case) -> None:
    got = tokenize(case.source)
    assert got == case.want
