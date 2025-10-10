"""Built-in ASCII rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar.expressions.choice import Choice
from pest.grammar.expressions.terminals import Range
from pest.grammar.expressions.terminals import String
from pest.grammar.rule import SILENT
from pest.grammar.rule import BuiltInRule
from pest.grammar.rule import Rule

if TYPE_CHECKING:
    from pest.grammar.expression import Expression

ASCII_RULE_MAP: dict[str, tuple[str, str] | list[tuple[str, str]]] = {
    "ASCII_DIGIT": ("0", "9"),
    "ASCII_NONZERO_DIGIT": ("1", "9"),
    "ASCII_BIN_DIGIT": ("0", "1"),
    "ASCII_OCT_DIGIT": ("0", "7"),
    "ASCII_HEX_DIGIT": [("0", "9"), ("a", "f"), ("A", "F")],
    "ASCII_ALPHANUMERIC": [("0", "9"), ("a", "z"), ("A", "Z")],
    "ASCII": ("\u0000", "\u007f"),
    "ASCII_ALPHA_LOWER": ("a", "z"),
    "ASCII_ALPHA_UPPER": ("A", "Z"),
    "ASCII_ALPHA": [("a", "z"), ("A", "Z")],
}


class ASCIIRule(BuiltInRule):
    """An ASCII character range rule."""

    def __init__(
        self, name: str, char_ranges: tuple[str, str] | list[tuple[str, str]]
    ) -> None:
        if isinstance(char_ranges, tuple):
            expr: Expression = Range(*char_ranges)
        else:
            expr = Choice(*[Range(*chars) for chars in char_ranges])
        super().__init__(name, expr, SILENT)

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 1
        return self


ASCII_RULES: dict[str, Rule] = {
    **{
        name: ASCIIRule(name, char_range) for name, char_range in ASCII_RULE_MAP.items()
    },
    "NEWLINE": BuiltInRule(
        "NEWLINE", Choice(String("\n"), String("\r\n"), String("\r")), SILENT
    ),
}
