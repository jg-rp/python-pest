import pytest

from pest.grammar.ac_index_any import index_any


def test_single_match() -> None:
    s = "the quick brown fox"
    assert index_any(s, ["quick"]) == 4


def test_multiple_candidates_returns_earliest() -> None:
    s = "foobar"
    assert index_any(s, ["bar", "foo"]) == 0


def test_overlapping_matches() -> None:
    s = "foobar"
    assert index_any(s, ["foobar", "foo"]) == 0


def test_match_after_start_offset() -> None:
    s = "foobarxbaz"
    assert index_any(s, ["foo", "baz"], start=6) == 7


def test_multiple_matches_same_position() -> None:
    s = "foobar"
    assert index_any(s, ["foobar", "foo"]) == 0


def test_match_at_end() -> None:
    s = "abcxyz"
    assert index_any(s, ["xyz"]) == 3


def test_no_match_raises() -> None:
    s = "hello world"
    with pytest.raises(ValueError, match=r"substrings not found"):
        index_any(s, ["not", "found"])


def test_empty_string_with_nonempty_patterns() -> None:
    s = ""
    with pytest.raises(ValueError, match=r"substrings not found"):
        index_any(s, ["foo", "bar"])


def test_empty_patterns_list() -> None:
    s = "foobar"
    with pytest.raises(ValueError, match=r"substrings not found"):
        index_any(s, [])
