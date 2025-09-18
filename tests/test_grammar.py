"""These tests are translated from Rust pest's `grammars.rs`.

https://github.com/pest-parser/pest/blob/master/vm/tests/grammar.rs.

See LICENSE_PEST.txt
"""

import pytest
from _pytest.fixtures import SubRequest

from pest import DEFAULT_OPTIMIZER
from pest import DUMMY_OPTIMIZER
from pest import Parser
from pest import PestParsingError


@pytest.fixture(scope="module", params=["not optimized", "optimized"])
def parser(request: SubRequest) -> Parser:
    optimizer = DEFAULT_OPTIMIZER if request.param == "optimized" else DUMMY_OPTIMIZER
    with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read(), optimizer=optimizer)


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


def test_repeat_max_once(parser: Parser) -> None:
    pairs = parser.parse("repeat_max", "abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_max",
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


def test_repeat_max_twice(parser: Parser) -> None:
    pairs = parser.parse("repeat_max", "abc abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_max",
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


# XXX: typo in Rust `repeat_max_thrice`?
# NOTE: `!parses_to` asserts EOF for every test case. We assert a partial parse.
def test_repeat_max_thrice(parser: Parser) -> None:
    pairs = parser.parse("repeat_max", "abc abc abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_max",
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


def test_repeat_max_atomic_once(parser: Parser) -> None:
    pairs = parser.parse("repeat_max_atomic", "abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_max_atomic",
            "span": {"str": "abc", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_repeat_max_atomic_twice(parser: Parser) -> None:
    pairs = parser.parse("repeat_max_atomic", "abcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_max_atomic",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [],
        }
    ]


# NOTE: `!parses_to` asserts EOF for every test case. We assert a partial parse.
def test_repeat_max_atomic_thrice(parser: Parser) -> None:
    pairs = parser.parse("repeat_max_atomic", "abcabcabc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_max_atomic",
            "span": {"str": "abcabc", "start": 0, "end": 6},
            "inner": [],
        }
    ]


def test_repeat_max_atomic_space(parser: Parser) -> None:
    pairs = parser.parse("repeat_max_atomic", "abc abc")
    # Not end of input
    assert pairs.as_list() == [
        {
            "rule": "repeat_max_atomic",
            "span": {"str": "abc", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_repeat_comment(parser: Parser) -> None:
    pairs = parser.parse("repeat_once", "abc$$$ $$$abc")
    assert pairs.as_list() == [
        {
            "rule": "repeat_once",
            "span": {"str": "abc$$$ $$$abc", "start": 0, "end": 13},
            "inner": [
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 0, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "string",
                    "span": {"str": "abc", "start": 10, "end": 13},
                    "inner": [],
                },
            ],
        }
    ]


def test_soi_at_start(parser: Parser) -> None:
    pairs = parser.parse("soi_at_start", "abc")
    assert pairs.as_list() == [
        {
            "rule": "soi_at_start",
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


def test_peek(parser: Parser) -> None:
    pairs = parser.parse("peek_", "0111")
    assert pairs.as_list() == [
        {
            "rule": "peek_",
            "span": {"str": "0111", "start": 0, "end": 4},
            "inner": [
                {
                    "rule": "range",
                    "span": {"str": "0", "start": 0, "end": 1},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "1", "start": 1, "end": 2},
                    "inner": [],
                },
            ],
        }
    ]


def test_peek_all(parser: Parser) -> None:
    pairs = parser.parse("peek_all", "0110")
    assert pairs.as_list() == [
        {
            "rule": "peek_all",
            "span": {"str": "0110", "start": 0, "end": 4},
            "inner": [
                {
                    "rule": "range",
                    "span": {"str": "0", "start": 0, "end": 1},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "1", "start": 1, "end": 2},
                    "inner": [],
                },
            ],
        }
    ]


def test_peek_slice_23(parser: Parser) -> None:
    pairs = parser.parse("peek_slice_23", "0123412")
    assert pairs.as_list() == [
        {
            "rule": "peek_slice_23",
            "span": {"str": "0123412", "start": 0, "end": 7},
            "inner": [
                {
                    "rule": "range",
                    "span": {"str": "0", "start": 0, "end": 1},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "1", "start": 1, "end": 2},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "2", "start": 2, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "3", "start": 3, "end": 4},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "4", "start": 4, "end": 5},
                    "inner": [],
                },
            ],
        }
    ]


def test_pop(parser: Parser) -> None:
    pairs = parser.parse("pop_", "0110")
    assert pairs.as_list() == [
        {
            "rule": "pop_",
            "span": {"str": "0110", "start": 0, "end": 4},
            "inner": [
                {
                    "rule": "range",
                    "span": {"str": "0", "start": 0, "end": 1},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "1", "start": 1, "end": 2},
                    "inner": [],
                },
            ],
        }
    ]


def test_pop_all(parser: Parser) -> None:
    pairs = parser.parse("pop_all", "0110")
    assert pairs.as_list() == [
        {
            "rule": "pop_all",
            "span": {"str": "0110", "start": 0, "end": 4},
            "inner": [
                {
                    "rule": "range",
                    "span": {"str": "0", "start": 0, "end": 1},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "1", "start": 1, "end": 2},
                    "inner": [],
                },
            ],
        }
    ]


def test_pop_fail(parser: Parser) -> None:
    pairs = parser.parse("pop_fail", "010")
    assert pairs.as_list() == [
        {
            "rule": "pop_fail",
            "span": {"str": "010", "start": 0, "end": 3},
            "inner": [
                {
                    "rule": "range",
                    "span": {"str": "0", "start": 0, "end": 1},
                    "inner": [],
                },
                {
                    "rule": "range",
                    "span": {"str": "1", "start": 1, "end": 2},
                    "inner": [],
                },
            ],
        }
    ]


def test_repeat_mutate_stack(parser: Parser) -> None:
    pairs = parser.parse("repeat_mutate_stack", "a,b,c,cba")
    assert pairs.as_list() == [
        {
            "rule": "repeat_mutate_stack",
            "span": {"str": "a,b,c,cba", "start": 0, "end": 9},
            "inner": [],
        }
    ]


def test_checkpoint_restore(parser: Parser) -> None:
    # XXX: make EOI non-silent?
    pairs = parser.parse("checkpoint_restore", "a")
    assert pairs.as_list() == [
        {
            "rule": "checkpoint_restore",
            "span": {"str": "a", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ascii_digits(parser: Parser) -> None:
    pairs = parser.parse("ascii_digits", "6")
    assert pairs.as_list() == [
        {
            "rule": "ascii_digits",
            "span": {"str": "6", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ascii_nonzero_digits(parser: Parser) -> None:
    pairs = parser.parse("ascii_nonzero_digits", "5")
    assert pairs.as_list() == [
        {
            "rule": "ascii_nonzero_digits",
            "span": {"str": "5", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ascii_bin_digits(parser: Parser) -> None:
    pairs = parser.parse("ascii_bin_digits", "1")
    assert pairs.as_list() == [
        {
            "rule": "ascii_bin_digits",
            "span": {"str": "1", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ascii_oct_digits(parser: Parser) -> None:
    pairs = parser.parse("ascii_oct_digits", "3")
    assert pairs.as_list() == [
        {
            "rule": "ascii_oct_digits",
            "span": {"str": "3", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ascii_hex_digits(parser: Parser) -> None:
    pairs = parser.parse("ascii_hex_digits", "6bC")
    assert pairs.as_list() == [
        {
            "rule": "ascii_hex_digits",
            "span": {"str": "6bC", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_ascii_alpha_lowers(parser: Parser) -> None:
    pairs = parser.parse("ascii_alpha_lowers", "a")
    assert pairs.as_list() == [
        {
            "rule": "ascii_alpha_lowers",
            "span": {"str": "a", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ascii_alpha_uppers(parser: Parser) -> None:
    pairs = parser.parse("ascii_alpha_uppers", "K")
    assert pairs.as_list() == [
        {
            "rule": "ascii_alpha_uppers",
            "span": {"str": "K", "start": 0, "end": 1},
            "inner": [],
        }
    ]


def test_ascii_alphas(parser: Parser) -> None:
    pairs = parser.parse("ascii_alphas", "wF")
    assert pairs.as_list() == [
        {
            "rule": "ascii_alphas",
            "span": {"str": "wF", "start": 0, "end": 2},
            "inner": [],
        }
    ]


def test_ascii_alphanumerics(parser: Parser) -> None:
    pairs = parser.parse("ascii_alphanumerics", "4jU")
    assert pairs.as_list() == [
        {
            "rule": "ascii_alphanumerics",
            "span": {"str": "4jU", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_asciis(parser: Parser) -> None:
    pairs = parser.parse("asciis", "x02")
    assert pairs.as_list() == [
        {
            "rule": "asciis",
            "span": {"str": "x02", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_newline(parser: Parser) -> None:
    pairs = parser.parse("newline", "\n\r\n\r")
    assert pairs.as_list() == [
        {
            "rule": "newline",
            "span": {"str": "\n\r\n\r", "start": 0, "end": 4},
            "inner": [],
        }
    ]


# NOTE: Our start and end indexes are in Unicode code points, not bytes.
def test_unicode(parser: Parser) -> None:
    pairs = parser.parse("unicode", "نامهای")
    assert pairs.as_list() == [
        {
            "rule": "unicode",
            "span": {
                "str": "\u0646\u0627\u0645\u0647\u0627\u06cc",
                "start": 0,
                "end": 6,
            },
            "inner": [],
        }
    ]


def test_shadow_builtin(parser: Parser) -> None:
    pairs = parser.parse("SYMBOL", "shadows builtin")
    assert pairs.as_list() == [
        {
            "rule": "SYMBOL",
            "span": {"str": "shadows builtin", "start": 0, "end": 15},
            "inner": [],
        }
    ]


def test_han(parser: Parser) -> None:
    pairs = parser.parse("han", "你好")
    assert pairs.as_list() == [
        {
            "rule": "han",
            "span": {"str": "\u4f60\u597d", "start": 0, "end": 2},
            "inner": [],
        }
    ]


def test_hangul(parser: Parser) -> None:
    pairs = parser.parse("hangul", "여보세요")
    assert pairs.as_list() == [
        {
            "rule": "hangul",
            "span": {"str": "\uc5ec\ubcf4\uc138\uc694", "start": 0, "end": 4},
            "inner": [],
        }
    ]


def test_hiragana(parser: Parser) -> None:
    pairs = parser.parse("hiragana", "こんにちは")
    assert pairs.as_list() == [
        {
            "rule": "hiragana",
            "span": {"str": "\u3053\u3093\u306b\u3061\u306f", "start": 0, "end": 5},
            "inner": [],
        }
    ]


def test_arabic(parser: Parser) -> None:
    pairs = parser.parse("arabic", "نامهای")
    assert pairs.as_list() == [
        {
            "rule": "arabic",
            "span": {
                "str": "\u0646\u0627\u0645\u0647\u0627\u06cc",
                "start": 0,
                "end": 6,
            },
            "inner": [],
        }
    ]


def test_emoji(parser: Parser) -> None:
    pairs = parser.parse("emoji", "👶")
    assert pairs.as_list() == [
        {
            "rule": "emoji",
            "span": {"str": "👶", "start": 0, "end": 1},
            "inner": [],
        }
    ]
