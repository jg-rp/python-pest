import pytest
from _pytest.fixtures import SubRequest

from pest import Parser


@pytest.fixture(scope="module", params=["not optimized", "optimized"])
def parser(request: SubRequest) -> Parser:
    with open("tests/grammars/json.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read(), optimize=request.param == "optimize")


def test_null_rule(parser: Parser) -> None:
    pairs = parser.parse("null", "null")
    assert pairs.as_list() == [
        {"rule": "null", "span": {"str": "null", "start": 0, "end": 4}, "inner": []}
    ]


def test_bool_rule(parser: Parser) -> None:
    pairs = parser.parse("bool", "false")
    assert pairs.as_list() == [
        {"rule": "bool", "span": {"str": "false", "start": 0, "end": 5}, "inner": []}
    ]


def test_number_rule_zero(parser: Parser) -> None:
    pairs = parser.parse("number", "0")
    assert pairs.as_list() == [
        {"rule": "number", "span": {"str": "0", "start": 0, "end": 1}, "inner": []}
    ]


def test_number_rule_float(parser: Parser) -> None:
    pairs = parser.parse("number", "100.001")
    assert pairs.as_list() == [
        {
            "rule": "number",
            "span": {"str": "100.001", "start": 0, "end": 7},
            "inner": [],
        }
    ]


def test_number_rule_float_exp(parser: Parser) -> None:
    pairs = parser.parse("number", "100.001E+100")
    assert pairs.as_list() == [
        {
            "rule": "number",
            "span": {"str": "100.001E+100", "start": 0, "end": 12},
            "inner": [],
        }
    ]


def test_number_rule_minus_zero(parser: Parser) -> None:
    pairs = parser.parse("number", "-0")
    assert pairs.as_list() == [
        {
            "rule": "number",
            "span": {"str": "-0", "start": 0, "end": 2},
            "inner": [],
        }
    ]


def test_string_rule_with_escape(parser: Parser) -> None:
    pairs = parser.parse("string", '"asd\\u0000\\""')
    assert pairs.as_list() == [
        {
            "rule": "string",
            "span": {"str": '"asd\\u0000\\""', "start": 0, "end": 13},
            "inner": [],
        }
    ]


def test_array_rule_empty(parser: Parser) -> None:
    pairs = parser.parse("array", "[ ]")
    assert pairs.as_list() == [
        {
            "rule": "array",
            "span": {"str": "[ ]", "start": 0, "end": 3},
            "inner": [],
        }
    ]


def test_array_rule(parser: Parser) -> None:
    pairs = parser.parse("array", '[0.0e1, false, null, "a", [0]]')
    assert pairs.as_list() == [
        {
            "rule": "array",
            "span": {"str": '[0.0e1, false, null, "a", [0]]', "start": 0, "end": 30},
            "inner": [
                {
                    "rule": "value",
                    "span": {"str": "0.0e1", "start": 1, "end": 6},
                    "inner": [
                        {
                            "rule": "number",
                            "span": {"str": "0.0e1", "start": 1, "end": 6},
                            "inner": [],
                        }
                    ],
                },
                {
                    "rule": "value",
                    "span": {"str": "false", "start": 8, "end": 13},
                    "inner": [
                        {
                            "rule": "bool",
                            "span": {"str": "false", "start": 8, "end": 13},
                            "inner": [],
                        }
                    ],
                },
                {
                    "rule": "value",
                    "span": {"str": "null", "start": 15, "end": 19},
                    "inner": [
                        {
                            "rule": "null",
                            "span": {"str": "null", "start": 15, "end": 19},
                            "inner": [],
                        }
                    ],
                },
                {
                    "rule": "value",
                    "span": {"str": '"a"', "start": 21, "end": 24},
                    "inner": [
                        {
                            "rule": "string",
                            "span": {"str": '"a"', "start": 21, "end": 24},
                            "inner": [],
                        }
                    ],
                },
                {
                    "rule": "value",
                    "span": {"str": "[0]", "start": 26, "end": 29},
                    "inner": [
                        {
                            "rule": "array",
                            "span": {"str": "[0]", "start": 26, "end": 29},
                            "inner": [
                                {
                                    "rule": "value",
                                    "span": {"str": "0", "start": 27, "end": 28},
                                    "inner": [
                                        {
                                            "rule": "number",
                                            "span": {
                                                "str": "0",
                                                "start": 27,
                                                "end": 28,
                                            },
                                            "inner": [],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                },
            ],
        }
    ]


def test_object_rule(parser: Parser) -> None:
    pairs = parser.parse("object", '{"a" : 3, "b" : [{}, 3]}')
    assert pairs.as_list() == [
        {
            "rule": "object",
            "span": {"str": '{"a" : 3, "b" : [{}, 3]}', "start": 0, "end": 24},
            "inner": [
                {
                    "rule": "pair",
                    "span": {"str": '"a" : 3', "start": 1, "end": 8},
                    "inner": [
                        {
                            "rule": "string",
                            "span": {"str": '"a"', "start": 1, "end": 4},
                            "inner": [],
                        },
                        {
                            "rule": "value",
                            "span": {"str": "3", "start": 7, "end": 8},
                            "inner": [
                                {
                                    "rule": "number",
                                    "span": {"str": "3", "start": 7, "end": 8},
                                    "inner": [],
                                }
                            ],
                        },
                    ],
                },
                {
                    "rule": "pair",
                    "span": {"str": '"b" : [{}, 3]', "start": 10, "end": 23},
                    "inner": [
                        {
                            "rule": "string",
                            "span": {"str": '"b"', "start": 10, "end": 13},
                            "inner": [],
                        },
                        {
                            "rule": "value",
                            "span": {"str": "[{}, 3]", "start": 16, "end": 23},
                            "inner": [
                                {
                                    "rule": "array",
                                    "span": {"str": "[{}, 3]", "start": 16, "end": 23},
                                    "inner": [
                                        {
                                            "rule": "value",
                                            "span": {
                                                "str": "{}",
                                                "start": 17,
                                                "end": 19,
                                            },
                                            "inner": [
                                                {
                                                    "rule": "object",
                                                    "span": {
                                                        "str": "{}",
                                                        "start": 17,
                                                        "end": 19,
                                                    },
                                                    "inner": [],
                                                }
                                            ],
                                        },
                                        {
                                            "rule": "value",
                                            "span": {
                                                "str": "3",
                                                "start": 21,
                                                "end": 22,
                                            },
                                            "inner": [
                                                {
                                                    "rule": "number",
                                                    "span": {
                                                        "str": "3",
                                                        "start": 21,
                                                        "end": 22,
                                                    },
                                                    "inner": [],
                                                }
                                            ],
                                        },
                                    ],
                                }
                            ],
                        },
                    ],
                },
            ],
        }
    ]


def test_example(parser: Parser) -> None:
    with open("tests/examples/example.json", encoding="utf-8") as fd:
        example = fd.read()

    parser.parse("json", example)


def test_line_col_span(parser: Parser) -> None:
    with open("tests/examples/example.json", encoding="utf-8") as fd:
        example = fd.read()

    with open("tests/examples/example.line-col.txt", encoding="utf-8") as fd:
        expected = fd.read()

    pairs = parser.parse("json", example)
    out: list[str] = []

    for pair in pairs.flatten():
        if not pair.children:
            span = pair.span()
            line, col = span.start_pos().line_col()
            span_str = str(span).replace("\n", "\\n")
            out.append(f"({line}:{col}) {span_str}\n")

    # XXX: I've removed the "one past the end" token from our copy of
    # example.line-col.txt.
    assert "".join(out).strip() == expected.strip()
