"""Built-in ASCII rules."""

from __future__ import annotations

from pest.grammar.expressions.rule import BuiltInRegexRangeRule
from pest.grammar.expressions.rule import BuiltInRegexRule

ASCII_RULE_MAP: dict[str, str | list[str] | tuple[str, str] | list[tuple[str, str]]] = {
    "ASCII_DIGIT": ("0", "9"),
    "ASCII_NONZERO_DIGIT": ("1", "9"),
    "ASCII_BIN_DIGIT": ("0", "1"),
    "ASCII_OCT_DIGIT": ("0", "7"),
    "ASCII_HEX_DIGIT": [("0", "9"), ("a", "f"), ("A", "F")],
    "ASCII_ALPHANUMERIC": [("0", "9"), ("a", "z"), ("A", "Z")],
    "ASCII": ("\u0000", "\u0074"),
    "ASCII_ALPHA_LOWER": ("a", "z"),
    "ASCII_ALPHA_UPPER": ("A", "Z"),
    "ASCII_ALPHA": [("a", "z"), ("A", "Z")],
    "NEWLINE": [r"\r?\n", r"\r"],
}

ASCII_RULES: dict[str, BuiltInRegexRule | BuiltInRegexRangeRule] = {}

for name, pattern in ASCII_RULE_MAP.items():
    if isinstance(pattern, str):
        ASCII_RULES[name] = BuiltInRegexRule(name, pattern)
    elif isinstance(pattern, list) and isinstance(pattern[0], str):
        ASCII_RULES[name] = BuiltInRegexRule(name, *pattern)
    elif isinstance(pattern, tuple):
        ASCII_RULES[name] = BuiltInRegexRangeRule(name, pattern)
    elif isinstance(pattern, list) and isinstance(pattern[0], tuple):
        ASCII_RULES[name] = BuiltInRegexRangeRule(name, *pattern)
