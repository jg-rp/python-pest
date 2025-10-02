"""These tests are translated from Rust pest's `grammars.rs`.

https://github.com/pest-parser/pest/blob/master/vm/tests/lists.rs.

See LICENSE_PEST.txt
"""

import pytest

from pest import Parser


@pytest.fixture(scope="module")
def grammar() -> str:
    with open("tests/grammars/lists.pest", encoding="utf-8") as fd:
        return fd.read()


def test_item(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []},
        {"rule": "EOI", "span": {"str": "", "start": 3, "end": 3}, "inner": []},
    ]


def test_items(parser: Parser) -> None:
    pairs = parser.parse("lists", "- a\n- b")
    assert pairs.as_list() == [
        {"rule": "item", "span": {"str": "a", "start": 2, "end": 3}, "inner": []},
        {"rule": "item", "span": {"str": "b", "start": 6, "end": 7}, "inner": []},
        {"rule": "EOI", "span": {"str": "", "start": 7, "end": 7}, "inner": []},
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
        {"rule": "EOI", "span": {"str": "", "start": 9, "end": 9}, "inner": []},
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
        {"rule": "EOI", "span": {"str": "", "start": 15, "end": 15}, "inner": []},
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
        {"rule": "EOI", "span": {"str": "", "start": 17, "end": 17}, "inner": []},
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
        {"rule": "EOI", "span": {"str": "", "start": 13, "end": 13}, "inner": []},
    ]
