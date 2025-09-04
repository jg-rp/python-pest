import pytest

from pest import Parser


@pytest.fixture(scope="module")
def parser() -> Parser:
    with open("tests/grammars/json.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read())


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
