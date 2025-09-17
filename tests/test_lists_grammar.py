"""These tests are translated from Rust pest's `grammars.rs`.

https://github.com/pest-parser/pest/blob/master/vm/tests/lists.rs.

See LICENSE_PEST.txt
"""

import pytest
from _pytest.fixtures import SubRequest

from pest import Parser


@pytest.fixture(scope="module", params=["not optimized", "optimized"])
def parser(request: SubRequest) -> Parser:
    with open("tests/grammars/lists.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read(), optimize=request.param == "optimized")


def test_item(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []}
    ]


def test_items(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a\n- b")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []},
        {"rule": "item", "span": {"str": "b", "start": 6, "end": 7}, "inner": []},
    ]


def test_children(parser: Parser) -> None:
    pairs = parser.parse("children", "  - b")
    assert pairs.as_list() == [
        {
            "rule": "children",
            "span": {"str": "  - b", "start": 0, "end": 5},
            "inner": [
                {
                    "rule": "item",
                    "span": {"str": "b", "start": 4, "end": 5},
                    "inner": [],
                }
            ],
        }
    ]


def test_nested_item(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a\n  - b")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []},
        {
            "rule": "children",
            "span": {"str": "  - b", "start": 4, "end": 9},
            "inner": [
                {
                    "rule": "item",
                    "span": {"str": "b", "start": 8, "end": 9},
                    "inner": [],
                }
            ],
        },
    ]


def test_nested_items(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a\n  - b\n  - c")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []},
        {
            "rule": "children",
            "span": {"str": "  - b\n  - c", "start": 4, "end": 15},
            "inner": [
                {
                    "rule": "item",
                    "span": {"str": "b", "start": 8, "end": 9},
                    "inner": [],
                },
                {
                    "rule": "item",
                    "span": {"str": "c", "start": 14, "end": 15},
                    "inner": [],
                },
            ],
        },
    ]


def test_nested_two_levels(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a\n  - b\n    - c")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []},
        {
            "rule": "children",
            "span": {"str": "  - b\n    - c", "start": 4, "end": 17},
            "inner": [
                {
                    "rule": "item",
                    "span": {"str": "b", "start": 8, "end": 9},
                    "inner": [],
                },
                {
                    "rule": "children",
                    "span": {"str": "    - c", "start": 10, "end": 17},
                    "inner": [
                        {
                            "rule": "item",
                            "span": {"str": "c", "start": 16, "end": 17},
                            "inner": [],
                        }
                    ],
                },
            ],
        },
    ]


def test_nested_then_not(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a\n  - b\n- c")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []},
        {
            "rule": "children",
            "span": {"str": "  - b", "start": 4, "end": 9},
            "inner": [
                {
                    "rule": "item",
                    "span": {"str": "b", "start": 8, "end": 9},
                    "inner": [],
                }
            ],
        },
        {"rule": "item", "span": {"str": "c", "start": 12, "end": 13}, "inner": []},
    ]
