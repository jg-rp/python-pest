# import operator
# from dataclasses import dataclass

# import pytest
# import regex

# from pest.grammar.expressions.lazy_regex import LazyRegexExpression


# @dataclass
# class Case:
#     description: str
#     positives: list[str]
#     negatives: list[str]
#     positive_ranges: list[tuple[str, str]]
#     negative_ranges: list[tuple[str, str]]
#     expected: str


# TEST_CASES = [
#     Case(
#         description="Empty inputs",
#         positives=[],
#         negatives=[],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected=".",
#     ),
#     Case(
#         description="Only positives (single char)",
#         positives=["a"],
#         negatives=[],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="[a]",
#     ),
#     Case(
#         description="Only positives (multiple chars)",
#         positives=["a", "b", "c"],
#         negatives=[],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="[a-c]",
#     ),
#     Case(
#         description="Only negatives (single char)",
#         positives=[],
#         negatives=["x"],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="[^x]",
#     ),
#     Case(
#         description="Only negatives (multiple chars)",
#         positives=[],
#         negatives=["x", "y"],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="[^x-y]",
#     ),
#     Case(
#         description="Positive range",
#         positives=[],
#         negatives=[],
#         positive_ranges=[("a", "z")],
#         negative_ranges=[],
#         expected="[a-z]",
#     ),
#     Case(
#         description="Multiple positive ranges",
#         positives=[],
#         negatives=[],
#         positive_ranges=[("0", "9"), ("a", "f")],
#         negative_ranges=[],
#         expected="[0-9a-f]",
#     ),
#     Case(
#         description="Negative range",
#         positives=[],
#         negatives=[],
#         positive_ranges=[],
#         negative_ranges=[("A", "Z")],
#         expected="[^A-Z]",
#     ),
#     Case(
#         description="Mixed: positives + negative ranges",
#         positives=["a", "b"],
#         negatives=[],
#         positive_ranges=[],
#         negative_ranges=[("0", "9")],
#         expected="[[a-b]--[0-9]]",
#     ),
#     Case(
#         description="Mixed: positives + positives ranges",
#         positives=["x"],
#         negatives=[],
#         positive_ranges=[("a", "z")],
#         negative_ranges=[],
#         expected="[a-z]",
#     ),
#     Case(
#         description="Mixed: negatives + positive ranges",
#         positives=[],
#         negatives=["!"],
#         positive_ranges=[("a", "z")],
#         negative_ranges=[],
#         expected="[[a-z]--[!]]",
#     ),
#     Case(
#         description="Complex: positives + negatives + ranges",
#         positives=["a"],
#         negatives=["z"],
#         positive_ranges=[("0", "9")],
#         negative_ranges=[("A", "Z")],
#         expected="[[0-9a]--[A-Zz]]",
#     ),
#     Case(
#         description="Multiple negative ranges",
#         positives=[],
#         negatives=[],
#         positive_ranges=[],
#         negative_ranges=[("0", "9"), ("A", "Z")],
#         expected="[^0-9A-Z]",
#     ),
#     Case(
#         description="Overlapping positive ranges that should simplify",
#         positives=[],
#         negatives=[],
#         positive_ranges=[("a", "f"), ("d", "z")],
#         negative_ranges=[],
#         expected="[a-z]",  # overlap between a–f and d–z collapses into a–z
#     ),
#     Case(
#         description="Only multi-character positives",
#         positives=["foo", "bar"],
#         negatives=[],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="(?:bar|foo)",  # alternation group
#     ),
#     Case(
#         description="Mixed single and multi-character positives",
#         positives=["x", "y", "foo"],
#         negatives=[],
#         positive_ranges=[("a", "c")],
#         negative_ranges=[],
#         expected="(?:[a-cx-y]|foo)",  # literals + character class
#     ),
#     Case(
#         description="Multi-character positives plus negatives",
#         positives=["foo", "bar"],
#         negatives=["z"],
#         positive_ranges=[("a", "f")],
#         negative_ranges=[],
#         expected="(?:[[a-f]--[z]]|bar|foo)",
#     ),
#     Case(
#         description="Only multi-character negatives",
#         positives=[],
#         negatives=["foo", "bar"],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="(?!foo|bar).",  # match any char, but not followed by foo/bar
#     ),
#     Case(
#         description="Single-char positives plus multi-character negatives",
#         positives=["a", "b"],
#         negatives=["foo"],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="(?!foo)[a-b]",
#     ),
#     Case(
#         description="Positive range plus multi-character negatives",
#         positives=[],
#         negatives=["end", "stop"],
#         positive_ranges=[("a", "z")],
#         negative_ranges=[],
#         expected="(?!end|stop)[a-z]",
#     ),
#     Case(
#         description="Mixed: multi-char positives and multi-char negatives",
#         positives=["foo", "bar"],
#         negatives=["baz"],
#         positive_ranges=[],
#         negative_ranges=[],
#         expected="(?!baz)(?:bar|foo)",  # alternation, restricted by lookahead
#     ),
#     Case(
#         description="Mixed: chars, ranges, and multi-char negatives",
#         positives=["x"],
#         negatives=["cat", "dog"],
#         positive_ranges=[("a", "c")],
#         negative_ranges=[("0", "9")],
#         expected="(?!cat|dog)[[a-cx]--[0-9]]",
#     ),
# ]


# @pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
# def test_build_regex_pattern(case: Case) -> None:
#     expr = LazyRegexExpression()
#     expr.positives = case.positives
#     expr.negatives = case.negatives
#     expr.positive_ranges = case.positive_ranges
#     expr.negative_ranges = case.negative_ranges
#     pattern = expr._build_pattern()  # noqa: SLF001
#     assert pattern == case.expected
#     assert isinstance(regex.compile(pattern, regex.VERSION1), regex.Pattern)
