"""These tests are translated from Rust pest's `reporting.rs`.

https://github.com/pest-parser/pest/blob/master/derive/tests/reporting.rs.

See LICENSE_PEST.txt
"""

import pytest

from pest import Parser, PestParsingError


@pytest.fixture(scope="module")
def parser() -> Parser:
    with open("tests/grammars/reporting.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read())


def test_choices(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices", "x")

    err = exec_info.value
    assert list(err.furthest_expected) == ["a", "b", "c"]
    assert list(err.furthest_unexpected) == []
    assert err.furthest_pos == 0


def test_choice_no_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_no_progress", "x")

    err = exec_info.value
    # XXX: we differ from Rust pest here
    assert list(err.furthest_expected) == ["a", "b", "c"]
    assert list(err.furthest_unexpected) == []
    assert err.furthest_pos == 0


def test_choice_a_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_a_progress", "a")

    err = exec_info.value
    assert list(err.furthest_expected) == ["a"]
    assert list(err.furthest_unexpected) == []
    assert err.furthest_pos == 1


def test_choice_b_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_b_progress", "b")

    err = exec_info.value
    assert list(err.furthest_expected) == ["b"]
    assert list(err.furthest_unexpected) == []
    assert err.furthest_pos == 1


def test_nested(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("level1", "x")

    err = exec_info.value
    assert list(err.furthest_expected) == ["a", "b", "c"]
    assert list(err.furthest_unexpected) == []
    assert err.furthest_pos == 0


def test_negative(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("negative", "x")

    err = exec_info.value
    assert list(err.furthest_expected) == []
    assert list(err.furthest_unexpected) == ["d"]
    assert err.furthest_pos == 0


def test_negative_match(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("negative_match", "x")

    err = exec_info.value
    assert list(err.furthest_expected) == ["b"]
    assert list(err.furthest_unexpected) == []
    assert err.furthest_pos == 0


def test_mixed(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("mixed", "x")

    err = exec_info.value
    assert list(err.furthest_expected) == ["a"]
    assert list(err.furthest_unexpected) == ["d"]
    assert err.furthest_pos == 0


def test_mixed_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("mixed_progress", "b")

    err = exec_info.value
    assert list(err.furthest_expected) == ["a"]
    assert list(err.furthest_unexpected) == []
    assert err.furthest_pos == 1
