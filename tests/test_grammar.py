"""These tests are translated from Rust pest's `grammars.rs`.

https://github.com/pest-parser/pest/blob/master/vm/tests/grammar.rs.

See LICENSE_PEST.txt
"""

import pytest

from pest import Parser
from pest import PestParsingError


@pytest.fixture(scope="module")
def parser() -> Parser:
    with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read())


def test_string_rule(parser: Parser) -> None:
    pairs = parser.parse("string", "abc")
    assert pairs.as_list() == [
        {"rule": "string", "span": {"str": "abc", "start": 0, "end": 3}, "inner": []}
    ]


def test_insensitive_rule(parser: Parser) -> None:
    pairs = parser.parse("insensitive", "aBC")
    assert pairs.as_list() == [
        {
            "rule": "insensitive",
            "span": {"str": "aBC", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_range_rule(parser: Parser) -> None:
    pairs = parser.parse("range", "6")
    assert pairs.as_list() == [
        {
            "rule": "range",
            "span": {"str": "6", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ident_rule(parser: Parser) -> None:
    pairs = parser.parse("ident", "abc")
    assert pairs.as_list() == [
        {
            "rule": "ident",
            "span": {"str": "abc", "start": 0, "end": 3},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                }
            ],
        }
    ]


def test_pos_pred_rule(parser: Parser) -> None:
    pairs = parser.parse("pos_pred", "abc")
    assert pairs.as_list() == [
        {
            "rule": "pos_pred",
            "span": {"str": "", "start": 0, "end": 0},
            "inner": [],
        }
    ]


def test_neg_pred_rule(parser: Parser) -> None:
    pairs = parser.parse("neg_pred", "")
    assert pairs.as_list() == [
        {
            "rule": "neg_pred",
            "span": {"str": "", "start": 0, "end": 0},
            "inner": [],
        }
    ]


def test_double_neg_pred_rule(parser: Parser) -> None:
    pairs = parser.parse("double_neg_pred", "abc")
    assert pairs.as_list() == [
        {
            "rule": "double_neg_pred",
            "span": {"str": "", "start": 0, "end": 0},
            "inner": [],
        }
    ]


def test_sequence_rule(parser: Parser) -> None:
    pairs = parser.parse("sequence", "abc   abc")
    assert pairs.as_list() == [
        {
            "rule": "sequence",
            "span": {"str": "abc   abc", "start": 0, "end": 9},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 6, "end": 9},
                    "inner": [],
                },
            ],
        }
    ]


def test_sequence_compound_rule(parser: Parser) -> None:
    pairs = parser.parse("sequence_compound", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "sequence_compound",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 3, "end": 6},
                    "inner": [],
                },
            ],
        }
    ]


def test_sequence_atomic_rule(parser: Parser) -> None:
    pairs = parser.parse("sequence_atomic", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "sequence_atomic",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [],
        }
    ]


def test_sequence_non_atomic_rule(parser: Parser) -> None:
    pairs = parser.parse("sequence_non_atomic", "abc   abc")
    assert pairs.as_list() == [
        {
            "rule": "sequence_non_atomic",
            "span": {"str": "abc   abc", "start": 0, "end": 9},
            "inner": [
                {
                    "rule": "sequence",
                    "span": {"str": "abc   abc", "start": 0, "end": 9},
                    "inner": [
                        {
                            "rule": "string",
                            "span": {"str": "abc", "start": 0, "end": 3},
                            "inner": [],
                        },
                        {
                            "rule": "string",
                            "span": {"str": "abc", "start": 6, "end": 9},
                            "inner": [],
                        },
                    ],
                }
            ],
        }
    ]


def test_atomic_space(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("sequence_atomic", "abc abc")


def test_sequence_atomic_compound_rule(parser: Parser) -> None:
    pairs = parser.parse("sequence_atomic_compound", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "sequence_atomic_compound",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [
                {
                    "rule": "sequence_compound",
                    "span": {"str": "abcabc", "start": 0, "end": 6},
                    "inner": [
                        {
                            "rule": "string",
                            "span": {"str": "abc", "start": 0, "end": 3},
                            "inner": [],
                        },
                        {
                            "rule": "string",
                            "span": {"str": "abc", "start": 3, "end": 6},
                            "inner": [],
                        },
                    ],
                }
            ],
        }
    ]


# TODO: sequence_compound_nested
