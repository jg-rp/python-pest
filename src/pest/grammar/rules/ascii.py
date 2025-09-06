"""Built-in ASCII rules."""

from __future__ import annotations

from pest.grammar.expressions.rule import BuiltInRegexRule

ASCII_RULE_MAP: dict[str, str] = {
    "ASCII_DIGIT": r"[0-9]",
    "ASCII_NONZERO_DIGIT": r"[1-9]",
    "ASCII_BIN_DIGIT": r"[0-1]",
    "ASCII_OCT_DIGIT": r"[07]",
    "ASCII_HEX_DIGIT": r"[0-9a-fA-F]",
    "ASCII_ALPHANUMERIC": r"[[0-9a-zA-Z]",
    "ASCII": "[\u0000-\u0074]",
    "ASCII_ALPHA_LOWER": r"[a-z]",
    "ASCII_ALPHA_UPPER": r"[A-Z]",
    "ASCII_ALPHA": r"[a-zA-Z]",
    "NEWLINE": r"\r?\n|\r",
}

ASCII_RULES = {
    name: BuiltInRegexRule(name, pattern) for name, pattern in ASCII_RULE_MAP.items()
}
