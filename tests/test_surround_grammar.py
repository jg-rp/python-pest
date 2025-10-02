"""These tests are translated from Rust pest's `grammars.rs`.

https://github.com/pest-parser/pest/blob/master/vm/tests/surround.rs.

See LICENSE_PEST.txt
"""

import pytest

from pest import Parser


@pytest.fixture(scope="module")
def grammar() -> str:
    with open("tests/grammars/surround.pest", encoding="utf-8") as fd:
        return fd.read()


def test_item(parser: Parser) -> None:
    pairs = parser.parse("Quote", "(abc)")
    assert pairs.as_list() == [
        {
            "rule": "QuoteChars",
            "span": {"str": "abc", "start": 1, "end": 4},
            "inner": [],
        }
    ]
