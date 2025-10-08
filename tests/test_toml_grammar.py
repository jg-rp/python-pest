import pytest

from .conftest import ParserLike as Parser


@pytest.fixture(scope="module")
def grammar() -> str:
    with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
        return fd.read()


def test_boolean_rule(parser: Parser) -> None:
    pairs = parser.parse("boolean", "true")
    assert pairs.dump() == [
        {"rule": "boolean", "span": {"str": "true", "start": 0, "end": 4}, "inner": []}
    ]


def test_integer_rule(parser: Parser) -> None:
    pairs = parser.parse("integer", "+1_000_0")
    assert pairs.dump() == [
        {
            "rule": "integer",
            "span": {"str": "+1_000_0", "start": 0, "end": 8},
            "inner": [],
        }
    ]


def test_float_rule(parser: Parser) -> None:
    pairs = parser.parse("float", "+1_0.0_1e+100")
    assert pairs.dump() == [
        {
            "rule": "float",
            "span": {"str": "+1_0.0_1e+100", "start": 0, "end": 13},
            "inner": [],
        }
    ]


def test_partial_time_rule(parser: Parser) -> None:
    pairs = parser.parse("partial_time", "12:34:56.000")
    assert pairs.dump() == [
        {
            "rule": "partial_time",
            "span": {"str": "12:34:56.000", "start": 0, "end": 12},
            "inner": [
                {
                    "rule": "time_hour",
                    "span": {"str": "12", "start": 0, "end": 2},
                    "inner": [],
                },
                {
                    "rule": "time_minute",
                    "span": {"str": "34", "start": 3, "end": 5},
                    "inner": [],
                },
                {
                    "rule": "time_second",
                    "span": {"str": "56", "start": 6, "end": 8},
                    "inner": [],
                },
                {
                    "rule": "time_secfrac",
                    "span": {"str": ".000", "start": 8, "end": 12},
                    "inner": [],
                },
            ],
        }
    ]


def test_full_date_rule(parser: Parser) -> None:
    pairs = parser.parse("full_date", "2001-12-13")
    assert pairs.dump() == [
        {
            "rule": "full_date",
            "span": {"str": "2001-12-13", "start": 0, "end": 10},
            "inner": [
                {
                    "rule": "date_fullyear",
                    "span": {"str": "2001", "start": 0, "end": 4},
                    "inner": [],
                },
                {
                    "rule": "date_month",
                    "span": {"str": "12", "start": 5, "end": 7},
                    "inner": [],
                },
                {
                    "rule": "date_mday",
                    "span": {"str": "13", "start": 8, "end": 10},
                    "inner": [],
                },
            ],
        }
    ]


def test_local_date_time_rule(parser: Parser) -> None:
    pairs = parser.parse("local_date_time", "2001-12-13T12:34:56.000")
    assert pairs.dump() == [
        {
            "rule": "local_date_time",
            "span": {"str": "2001-12-13T12:34:56.000", "start": 0, "end": 23},
            "inner": [
                {
                    "rule": "full_date",
                    "span": {"str": "2001-12-13", "start": 0, "end": 10},
                    "inner": [
                        {
                            "rule": "date_fullyear",
                            "span": {"str": "2001", "start": 0, "end": 4},
                            "inner": [],
                        },
                        {
                            "rule": "date_month",
                            "span": {"str": "12", "start": 5, "end": 7},
                            "inner": [],
                        },
                        {
                            "rule": "date_mday",
                            "span": {"str": "13", "start": 8, "end": 10},
                            "inner": [],
                        },
                    ],
                },
                {
                    "rule": "partial_time",
                    "span": {"str": "12:34:56.000", "start": 11, "end": 23},
                    "inner": [
                        {
                            "rule": "time_hour",
                            "span": {"str": "12", "start": 11, "end": 13},
                            "inner": [],
                        },
                        {
                            "rule": "time_minute",
                            "span": {"str": "34", "start": 14, "end": 16},
                            "inner": [],
                        },
                        {
                            "rule": "time_second",
                            "span": {"str": "56", "start": 17, "end": 19},
                            "inner": [],
                        },
                        {
                            "rule": "time_secfrac",
                            "span": {"str": ".000", "start": 19, "end": 23},
                            "inner": [],
                        },
                    ],
                },
            ],
        }
    ]


def test_date_time_rule(parser: Parser) -> None:
    pairs = parser.parse("date_time", "2001-12-13T12:34:56.000Z")
    assert pairs.dump() == [
        {
            "rule": "date_time",
            "span": {"str": "2001-12-13T12:34:56.000Z", "start": 0, "end": 24},
            "inner": [
                {
                    "rule": "full_date",
                    "span": {"str": "2001-12-13", "start": 0, "end": 10},
                    "inner": [
                        {
                            "rule": "date_fullyear",
                            "span": {"str": "2001", "start": 0, "end": 4},
                            "inner": [],
                        },
                        {
                            "rule": "date_month",
                            "span": {"str": "12", "start": 5, "end": 7},
                            "inner": [],
                        },
                        {
                            "rule": "date_mday",
                            "span": {"str": "13", "start": 8, "end": 10},
                            "inner": [],
                        },
                    ],
                },
                {
                    "rule": "full_time",
                    "span": {"str": "12:34:56.000Z", "start": 11, "end": 24},
                    "inner": [
                        {
                            "rule": "partial_time",
                            "span": {"str": "12:34:56.000", "start": 11, "end": 23},
                            "inner": [
                                {
                                    "rule": "time_hour",
                                    "span": {"str": "12", "start": 11, "end": 13},
                                    "inner": [],
                                },
                                {
                                    "rule": "time_minute",
                                    "span": {"str": "34", "start": 14, "end": 16},
                                    "inner": [],
                                },
                                {
                                    "rule": "time_second",
                                    "span": {"str": "56", "start": 17, "end": 19},
                                    "inner": [],
                                },
                                {
                                    "rule": "time_secfrac",
                                    "span": {"str": ".000", "start": 19, "end": 23},
                                    "inner": [],
                                },
                            ],
                        },
                        {
                            "rule": "time_offset",
                            "span": {"str": "Z", "start": 23, "end": 24},
                            "inner": [],
                        },
                    ],
                },
            ],
        }
    ]


def test_literal_rule(parser: Parser) -> None:
    pairs = parser.parse("literal", "'\"'")
    assert pairs.dump() == [
        {"rule": "literal", "span": {"str": "'\"'", "start": 0, "end": 3}, "inner": []}
    ]


def test_multi_line_literal_rule(parser: Parser) -> None:
    pairs = parser.parse("multi_line_literal", "'''\"'''")
    assert pairs.dump() == [
        {
            "rule": "multi_line_literal",
            "span": {"str": "'''\"'''", "start": 0, "end": 7},
            "inner": [],
        }
    ]


def test_string_rule(parser: Parser) -> None:
    pairs = parser.parse("string", '"\\n"')
    assert pairs.dump() == [
        {"rule": "string", "span": {"str": '"\\n"', "start": 0, "end": 4}, "inner": []}
    ]


def test_multi_line_string_rule(parser: Parser) -> None:
    pairs = parser.parse("multi_line_string", '""" \\n """')
    assert pairs.dump() == [
        {
            "rule": "multi_line_string",
            "span": {"str": '""" \\n """', "start": 0, "end": 10},
            "inner": [],
        }
    ]


def test_empty_array(parser: Parser) -> None:
    pairs = parser.parse("array", "[ ]")
    assert pairs.dump() == [
        {"rule": "array", "span": {"str": "[ ]", "start": 0, "end": 3}, "inner": []}
    ]


def test_array_rule(parser: Parser) -> None:
    pairs = parser.parse("array", "['', 2017-08-09, 20.0]")
    assert pairs.dump() == [
        {
            "rule": "array",
            "span": {"str": "['', 2017-08-09, 20.0]", "start": 0, "end": 22},
            "inner": [
                {
                    "rule": "literal",
                    "span": {"str": "''", "start": 1, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "full_date",
                    "span": {"str": "2017-08-09", "start": 5, "end": 15},
                    "inner": [
                        {
                            "rule": "date_fullyear",
                            "span": {"str": "2017", "start": 5, "end": 9},
                            "inner": [],
                        },
                        {
                            "rule": "date_month",
                            "span": {"str": "08", "start": 10, "end": 12},
                            "inner": [],
                        },
                        {
                            "rule": "date_mday",
                            "span": {"str": "09", "start": 13, "end": 15},
                            "inner": [],
                        },
                    ],
                },
                {
                    "rule": "float",
                    "span": {"str": "20.0", "start": 17, "end": 21},
                    "inner": [],
                },
            ],
        }
    ]


def test_inline_table_rule(parser: Parser) -> None:
    pairs = parser.parse("inline_table", "{ a = 'b' }")
    assert pairs.dump() == [
        {
            "rule": "inline_table",
            "span": {"str": "{ a = 'b' }", "start": 0, "end": 11},
            "inner": [
                {
                    "rule": "pair",
                    "span": {"str": "a = 'b'", "start": 2, "end": 9},
                    "inner": [
                        {
                            "rule": "key",
                            "span": {"str": "a", "start": 2, "end": 3},
                            "inner": [],
                        },
                        {
                            "rule": "literal",
                            "span": {"str": "'b'", "start": 6, "end": 9},
                            "inner": [],
                        },
                    ],
                }
            ],
        }
    ]


def test_table_rule(parser: Parser) -> None:
    pairs = parser.parse("table", "[a.b]\nc = 'd'")
    assert pairs.dump() == [
        {
            "rule": "table",
            "span": {"str": "[a.b]\nc = 'd'", "start": 0, "end": 13},
            "inner": [
                {
                    "rule": "key",
                    "span": {"str": "a", "start": 1, "end": 2},
                    "inner": [],
                },
                {
                    "rule": "key",
                    "span": {"str": "b", "start": 3, "end": 4},
                    "inner": [],
                },
                {
                    "rule": "pair",
                    "span": {"str": "c = 'd'", "start": 6, "end": 13},
                    "inner": [
                        {
                            "rule": "key",
                            "span": {"str": "c", "start": 6, "end": 7},
                            "inner": [],
                        },
                        {
                            "rule": "literal",
                            "span": {"str": "'d'", "start": 10, "end": 13},
                            "inner": [],
                        },
                    ],
                },
            ],
        }
    ]


def test_array_table_rule(parser: Parser) -> None:
    pairs = parser.parse("array_table", "[[a.b]]\nc = 'd'")
    assert pairs.dump() == [
        {
            "rule": "array_table",
            "span": {"str": "[[a.b]]\nc = 'd'", "start": 0, "end": 15},
            "inner": [
                {
                    "rule": "key",
                    "span": {"str": "a", "start": 2, "end": 3},
                    "inner": [],
                },
                {
                    "rule": "key",
                    "span": {"str": "b", "start": 4, "end": 5},
                    "inner": [],
                },
                {
                    "rule": "pair",
                    "span": {"str": "c = 'd'", "start": 8, "end": 15},
                    "inner": [
                        {
                            "rule": "key",
                            "span": {"str": "c", "start": 8, "end": 9},
                            "inner": [],
                        },
                        {
                            "rule": "literal",
                            "span": {"str": "'d'", "start": 12, "end": 15},
                            "inner": [],
                        },
                    ],
                },
            ],
        }
    ]


def test_example(parser: Parser) -> None:
    with open("tests/examples/example.toml", encoding="utf-8") as fd:
        example = fd.read()

    parser.parse("toml", example)
