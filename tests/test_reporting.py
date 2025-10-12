"""These tests are translated from Rust pest's `reporting.rs`.

https://github.com/pest-parser/pest/blob/master/derive/tests/reporting.rs.

See LICENSE_PEST.txt
"""

import pytest

from pest import Parser
from pest import PestParsingError


@pytest.fixture(scope="module")
def grammar() -> str:
    with open("tests/grammars/reporting.pest", encoding="utf-8") as fd:
        return fd.read()


def test_choices(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices", "x")

    err = exec_info.value
    state = err.state
    assert list(state.furthest_expected) == ["a", "b", "c"]
    assert list(state.furthest_unexpected) == []
    assert state.furthest_pos == 0


def test_choice_no_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_no_progress", "x")

    err = exec_info.value
    state = err.state
    # NOTE: we differ from Rust pest here
    assert list(state.furthest_expected) == ["a", "b", "c"]
    assert list(state.furthest_unexpected) == []
    assert state.furthest_pos == 0


def test_choice_a_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_a_progress", "a")

    err = exec_info.value
    state = err.state
    assert list(state.furthest_expected) == ["a"]
    assert list(state.furthest_unexpected) == []
    assert state.furthest_pos == 1


def test_choice_b_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_b_progress", "b")

    err = exec_info.value
    state = err.state
    assert list(state.furthest_expected) == ["b"]
    assert list(state.furthest_unexpected) == []
    assert state.furthest_pos == 1


def test_nested(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("level1", "x")

    err = exec_info.value
    state = err.state
    assert list(state.furthest_expected) == ["a", "b", "c"]
    assert list(state.furthest_unexpected) == []
    assert state.furthest_pos == 0


# TODO: negative
