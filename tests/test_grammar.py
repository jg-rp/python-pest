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


def test_sequence_compound_nested_rule(parser: Parser) -> None:
    pairs = parser.parse("sequence_compound_nested", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "sequence_compound_nested",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [
                {
                    "rule": "sequence_nested",
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


def test_sequence_compound_nested_space(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("sequence_compound_nested", "abc abc")


def test_choice_string(parser: Parser) -> None:
    pairs = parser.parse("choice", "abc")
    assert pairs.as_list() == [
        {
            "rule": "choice",
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


def test_choice_range(parser: Parser) -> None:
    pairs = parser.parse("choice", "0")
    assert pairs.as_list() == [
        {
            "rule": "choice",
            "span": {"str": "0", "start": 0, "end": 1},
            "inner": [
                {
                    "rule": "range",
                    "span": {"str": "0", "start": 0, "end": 1},
                    "inner": [],
                }
            ],
        }
    ]


def test_optional_string(parser: Parser) -> None:
    pairs = parser.parse("optional", "abc")
    assert pairs.as_list() == [
        {
            "rule": "optional",
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


def test_optional_empty(parser: Parser) -> None:
    pairs = parser.parse("optional", "")
    assert pairs.as_list() == [
        {"rule": "optional", "span": {"str": "", "start": 0, "end": 0}, "inner": []}
    ]


def test_repeat_empty(parser: Parser) -> None:
    pairs = parser.parse("repeat", "")
    assert pairs.as_list() == [
        {"rule": "repeat", "span": {"str": "", "start": 0, "end": 0}, "inner": []}
    ]


def test_repeat_strings(parser: Parser) -> None:
    pairs = parser.parse("repeat", "abc   abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat",
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


def test_repeat_atomic_empty(parser: Parser) -> None:
    pairs = parser.parse("repeat_atomic", "")
    assert pairs.as_list() == [
        {
            "rule": "repeat_atomic",
            "span": {"str": "", "start": 0, "end": 0},
            "inner": [],
        }
    ]


def test_repeat_atomic_strings(parser: Parser) -> None:
    pairs = parser.parse("repeat_atomic", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_atomic",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [],
        }
    ]


# XXX: We differ from Rust pest here.
# I think `!parses_to` asserts EOF for every test case.
def test_repeat_atomic_space(parser: Parser) -> None:
    pairs = parser.parse("repeat_atomic", "abc abc")
    # We match the first `abc` then stop at the space.
    assert pairs.as_list() == [
        {
            "rule": "repeat_atomic",
            "span": {"str": "abc", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_repeat_once_empty(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("repeat_once", "")


def test_repeat_once_strings(parser: Parser) -> None:
    pairs = parser.parse("repeat_once", "abc   abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_once",
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


def test_repeat_once_atomic_empty(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("repeat_once_atomic", "")


def test_repeat_once_atomic_strings(parser: Parser) -> None:
    pairs = parser.parse("repeat_once_atomic", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_once_atomic",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [],
        }
    ]


# XXX: We differ from Rust pest here.
# I think `!parses_to` asserts EOF for every test case.
def test_repeat_once_atomic_space(parser: Parser) -> None:
    pairs = parser.parse("repeat_once_atomic", "abc abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_once_atomic",
            "span": {"str": "abc", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_repeat_min_max_twice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min_max", "abc abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min_max",
            "span": {"str": "abc abc", "start": 0, "end": 7},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 4, "end": 7},
                    "inner": [],
                },
            ],
        }
    ]


def test_repeat_min_max_thrice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min_max", "abc abc abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min_max",
            "span": {"str": "abc abc abc", "start": 0, "end": 11},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 4, "end": 7},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 8, "end": 11},
                    "inner": [],
                },
            ],
        }
    ]


def test_repeat_min_max_atomic_twice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min_max_atomic", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min_max_atomic",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [],
        }
    ]


def test_repeat_min_max_atomic_thrice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min_max_atomic", "abcabcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min_max_atomic",
            "span": {"str": "abcabcabc", "start": 0, "end": 9},
            "inner": [],
        }
    ]


def test_repeat_min_max_atomic_space(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("repeat_min_max_atomic", "abc abc")


def test_repeat_exact(parser: Parser) -> None:
    pairs = parser.parse("repeat_exact", "abc abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_exact",
            "span": {"str": "abc abc", "start": 0, "end": 7},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 4, "end": 7},
                    "inner": [],
                },
            ],
        }
    ]


def test_repeat_min_once(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("repeat_min", "abc")


def test_repeat_min_twice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min", "abc abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min",
            "span": {"str": "abc abc", "start": 0, "end": 7},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 4, "end": 7},
                    "inner": [],
                },
            ],
        }
    ]


def test_repeat_min_thrice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min", "abc abc  abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min",
            "span": {"str": "abc abc  abc", "start": 0, "end": 12},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 4, "end": 7},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 9, "end": 12},
                    "inner": [],
                },
            ],
        }
    ]


def test_repeat_min_atomic_once(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("repeat_min_atomic", "abc")


def test_repeat_min_atomic_twice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min_atomic", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min_atomic",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [],
        }
    ]


def test_repeat_min_atomic_thrice(parser: Parser) -> None:
    pairs = parser.parse("repeat_min_atomic", "abcabcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_min_atomic",
            "span": {"str": "abcabcabc", "start": 0, "end": 9},
            "inner": [],
        }
    ]


def test_repeat_min_atomic_space(parser: Parser) -> None:
    with pytest.raises(PestParsingError):
        parser.parse("repeat_min_atomic", "abc abc")


# TODO: repeat_max_once
