"""The choice (`|`) operator and an optimized regex choice expression."""

from __future__ import annotations

from enum import Enum
from enum import auto
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import Self
from typing import TypeAlias

import regex as re

from pest.grammar import Expression
from pest.grammar.expression import Match
from pest.grammar.expression import RegexExpression
from pest.grammar.rules.unicode import UnicodePropertyRule

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.state import ParserState


class Choice(Expression):
    """An expression that matches a one of a choice of sub-expressions.

    This corresponds to the `|` operator in pest.
    """

    __slots__ = ("expressions",)

    def __init__(self, *expressions: Expression):
        super().__init__(None)
        self.expressions = list(expressions)

    def __str__(self) -> str:
        choice = " | ".join(str(expr) for expr in self.expressions)
        return f"{self.tag_str()}{choice}"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        for expr in self.expressions:
            state.snapshot()
            result = state.parse(expr, start, self.tag)
            if result:
                state.ok()
                return result

            state.restore()
        return None

    def generate(self, gen: Builder, pairs_var: str) -> None:
        """Emit Python code for a choice expression."""
        tmp_pairs = gen.new_temp("children")
        matched = gen.new_temp("matched")

        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln(f"{matched} = False")

        for branch in self.expressions:
            cp = gen.new_temp("cp")
            gen.writeln(f"if not {matched}:")
            with gen.block():
                gen.writeln(f"{cp} = state.checkpoint()")
                gen.writeln("try:")
                with gen.block():
                    branch.generate(gen, tmp_pairs)
                    gen.writeln(f"{matched} = True")
                gen.writeln("except ParseError:")
                with gen.block():
                    gen.writeln(f"state.restore({cp})")
                    gen.writeln(f"{tmp_pairs}.clear()")

        gen.writeln(f"if not {matched}:")
        with gen.block():
            gen.writeln('raise ParseError("no choice matched")')

        gen.writeln(f"{pairs_var}.extend({tmp_pairs})")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return self.expressions

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)


class ChoiceCase(Enum):
    """Lazy choice regex item case."""

    SENSITIVE = auto()
    INSENSITIVE = auto()


class ChoiceLiteral(NamedTuple):
    """Lazy choice regex literal."""

    value: str
    case: ChoiceCase


class ChoiceRange(NamedTuple):
    """Lazy choice regex character range."""

    start: str
    end: str


ChoiceChoice: TypeAlias = ChoiceLiteral | ChoiceRange | UnicodePropertyRule


class LazyChoiceRegex(Expression):
    """An optimized expression for matching a set of choices using a single regex.

    Supports single-character literals, multi-character literals (case-sensitive or
    insensitive), character ranges, and Unicode property rules.

    Args:
        choices: Optional initial list of choices to match.
    """

    __slots__ = ("_choices", "_compiled")

    def __init__(self, choices: list[ChoiceChoice] | None = None):
        super().__init__(None)
        self._choices = choices or []
        self._compiled: re.Pattern[str] | None = None

    def __str__(self) -> str:
        return f"/{self.pattern.pattern!r}/"

    @property
    def pattern(self) -> re.Pattern[str]:
        """The compiled regex."""
        if self._compiled is None:
            self._compiled = re.compile(self.build_optimized_pattern(), re.VERSION1)
        return self._compiled

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        if match := self.pattern.match(state.input, start):
            return [Match(None, match.end())]
        return None

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 0
        return self

    def update(self, *choices: ChoiceChoice) -> LazyChoiceRegex:
        """Add choices to this regex and return self."""
        self._choices.extend(choices)
        return self

    def copy(self, *choices: ChoiceChoice) -> LazyChoiceRegex:
        """Return a new LazyChoiceRegex with current and additional choices."""
        return LazyChoiceRegex(self._choices).update(*choices)

    def build_optimized_pattern(self) -> str:
        """Return a regex pattern matching all collected choices."""
        return build_optimized_pattern(self._choices)


def build_optimized_pattern(choices: list[ChoiceChoice]) -> str:  # noqa: PLR0912
    """Build a regex pattern that matches any of the given choices."""
    if not choices:
        return ""

    char_class_parts: list[str] = []  # for single-char literals
    ranges: list[tuple[str, str]] = []  # for character ranges
    multi_sensitive: list[str] = []  # for multi-char sensitive literals
    insensitive_parts: list[str] = []  # for insensitive literals (scoped flag)
    unicode_props: list[str] = []  # for UnicodeProperty patterns

    for choice in choices:
        match choice:
            case UnicodePropertyRule(expression=RegexExpression(pattern=pattern)):
                unicode_props.append(pattern)
            case ChoiceLiteral(value=val, case=ChoiceCase.INSENSITIVE) if len(val) == 1:
                char_class_parts.append(val.upper())
                char_class_parts.append(val.lower())
            case ChoiceLiteral(value=val, case=ChoiceCase.INSENSITIVE):
                insensitive_parts.append(f"(?i:{re.escape(val)})")
            case ChoiceLiteral(value=val, case=ChoiceCase.SENSITIVE) if len(val) == 1:
                char_class_parts.append(val)
            case ChoiceLiteral(value=val, case=ChoiceCase.SENSITIVE):
                multi_sensitive.append(re.escape(val))
            case ChoiceRange(start, end):
                ranges.append((start, end))
            case _:
                raise ValueError(f"Unrecognized choice: {choice}")

    parts = []
    if multi_sensitive:
        parts.extend(multi_sensitive)
    if insensitive_parts:
        parts.extend(insensitive_parts)
    if unicode_props:
        parts.extend(unicode_props)
    if char_class_parts or ranges:
        parts.append(_optimize_char_class(char_class_parts, ranges))

    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return "(?:" + "|".join(parts) + ")"


def _optimize_char_class(singles: list[str], ranges: list[tuple[str, str]]) -> str:
    # Normalize ranges into codepoints
    norm_ranges: list[tuple[int, int]] = []
    for start, end in ranges:
        s_cp, e_cp = ord(start), ord(end)
        if s_cp > e_cp:
            s_cp, e_cp = e_cp, s_cp
        norm_ranges.append((s_cp, e_cp))

    # Merge ranges
    norm_ranges.sort()
    merged: list[list[int]] = []
    for s, e in norm_ranges:
        if not merged or s > merged[-1][1] + 1:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)

    # Drop singles covered by ranges
    singles = sorted(
        {c for c in singles if all(not (s <= ord(c) <= e) for s, e in merged)}
    )

    # Build final pattern
    parts_out = [re.escape(c) for c in singles]
    for s, e in merged:
        if s == e:
            parts_out.append(re.escape(chr(s)))
        else:
            parts_out.append(f"{re.escape(chr(s))}-{re.escape(chr(e))}")
    return "[" + "".join(parts_out) + "]"
