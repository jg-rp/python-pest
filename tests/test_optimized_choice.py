import regex as re

from pest.grammar.expressions.choice import ChoiceCase
from pest.grammar.expressions.choice import LazyChoiceRegex
from pest.grammar.expressions.choice import _Choice  # noqa: F401
from pest.grammar.expressions.choice import build_optimized_pattern
from pest.grammar.rules.unicode import UnicodePropertyRule


def test_single_sensitive_literal() -> None:
    pattern = build_optimized_pattern([("a", ChoiceCase.SENSITIVE)])
    regex = re.compile(pattern)
    assert regex.fullmatch("a")
    assert not regex.fullmatch("A")


def test_single_insensitive_literal() -> None:
    pattern = build_optimized_pattern([("a", ChoiceCase.INSENSITIVE)])
    regex = re.compile(pattern)
    assert regex.fullmatch("a")
    assert regex.fullmatch("A")


def test_range() -> None:
    pattern = build_optimized_pattern([("a", "z")])
    regex = re.compile(pattern)
    assert regex.fullmatch("a")
    assert regex.fullmatch("m")
    assert regex.fullmatch("z")
    assert not regex.fullmatch("A")


def test_multi_char_literal() -> None:
    pattern = build_optimized_pattern([("abc", ChoiceCase.SENSITIVE)])
    regex = re.compile(pattern)
    assert regex.fullmatch("abc")
    assert not regex.fullmatch("ABC")


def test_unicode_property() -> None:
    greek = UnicodePropertyRule("\\p{Script=Greek}", "MOCK_PROP")
    pattern = build_optimized_pattern([greek])
    regex = re.compile(pattern)
    assert regex.fullmatch("α")  # Greek alpha
    assert not regex.fullmatch("a")


def test_mixed_choices() -> None:
    greek = UnicodePropertyRule("\\p{Script=Greek}", "MOCK_PROP")
    choices: list[_Choice] = [
        ("abc", ChoiceCase.SENSITIVE),
        ("x", ChoiceCase.INSENSITIVE),
        ("0", "9"),
        greek,
    ]
    pattern = build_optimized_pattern(choices)
    regex = re.compile(pattern)

    assert regex.fullmatch("abc")
    assert regex.fullmatch("x")
    assert regex.fullmatch("X")
    assert regex.fullmatch("5")
    assert regex.fullmatch("β")
    assert not regex.fullmatch("zzz")
    assert pattern == r"(?:[Xx0-9]|abc|\p{Script=Greek})"


def test_duplicate_characters_collapsed_exact() -> None:
    pattern = build_optimized_pattern(
        [
            ("a", ChoiceCase.SENSITIVE),
            ("a", ChoiceCase.SENSITIVE),
        ]
    )
    assert pattern == "[a]"


def test_overlapping_ranges_collapsed_exact() -> None:
    pattern = build_optimized_pattern(
        [
            ("a", "c"),
            ("b", "d"),
        ]
    )
    assert pattern == "[a-d]"


def test_adjacent_ranges_merged() -> None:
    pattern = build_optimized_pattern(
        [
            ("a", "c"),
            ("d", "f"),
        ]
    )
    assert pattern == "[a-f]"


def test_single_within_range_removed() -> None:
    pattern = build_optimized_pattern(
        [
            ("a", "z"),
            ("m", ChoiceCase.SENSITIVE),
        ]
    )
    assert pattern == "[a-z]"


def test_lazy_choice_regex_initial_and_update() -> None:
    greek = UnicodePropertyRule("\\p{Script=Greek}", "MOCK_PROP")
    regex_builder = LazyChoiceRegex([("a", ChoiceCase.SENSITIVE)])
    regex_builder.update(("0", "9"), ("x", ChoiceCase.INSENSITIVE), greek)

    pattern = regex_builder.build_optimized_pattern()
    compiled = re.compile(pattern)

    assert compiled.fullmatch("a")
    assert compiled.fullmatch("5")
    assert compiled.fullmatch("x")
    assert compiled.fullmatch("X")
    assert compiled.fullmatch("β")


def test_lazy_choice_regex_empty_then_update() -> None:
    regex_builder = LazyChoiceRegex()
    regex_builder.update(("b", ChoiceCase.SENSITIVE))
    assert regex_builder.build_optimized_pattern() == "[b]"

    regex_builder.update(("c", ChoiceCase.SENSITIVE))
    pattern = regex_builder.build_optimized_pattern()
    assert pattern == "[bc]"


def test_large_range_and_literals_merging() -> None:
    regex_builder = LazyChoiceRegex()
    regex_builder.update(("a", "f"))
    regex_builder.update(("g", "k"))
    regex_builder.update(("c", "h"))
    regex_builder.update(("d", ChoiceCase.SENSITIVE))
    regex_builder.update(("j", ChoiceCase.SENSITIVE))
    regex_builder.update(("A", ChoiceCase.INSENSITIVE))

    pattern = regex_builder.build_optimized_pattern()
    assert pattern == "[Aa-k]"


def test_large_mixed_literals_and_ranges() -> None:
    regex_builder = LazyChoiceRegex()
    for ch in ["a", "d", "g", "j", "m", "p", "s", "v"]:
        start = ch
        end = chr(ord(ch) + 2)
        regex_builder.update((start, end))

    pattern = regex_builder.build_optimized_pattern()
    assert pattern == "[a-x]"
