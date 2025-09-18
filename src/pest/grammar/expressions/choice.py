"""The choice (`|`) operator."""

from __future__ import annotations

from enum import Enum
from enum import auto
from typing import TYPE_CHECKING
from typing import Iterator
from typing import TypeAlias

import regex as re
from typing_extensions import Self

from pest.grammar import Expression
from pest.grammar.expression import RegexExpression
from pest.grammar.expression import Success
from pest.grammar.rules.unicode import UnicodePropertyRule

if TYPE_CHECKING:
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

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        for expr in self.expressions:
            state.snapshot()
            result = list(state.parse(expr, start))
            if result:
                state.ok()
                yield from result
                break
            else:
                state.restore()

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


_Range: TypeAlias = tuple[str, str]  # Character range
_Literal: TypeAlias = tuple[str, ChoiceCase]  # str could be any length
_Choice: TypeAlias = _Literal | _Range | UnicodePropertyRule


class LazyChoiceRegex(Expression):
    """An optimized choice expression."""

    __slots__ = ("_choices", "_compiled")

    def __init__(self, choices: list[_Choice] | None = None):
        super().__init__(None)
        self._choices = choices or []
        self._compiled: re.Pattern[str] | None = None

    @property
    def pattern(self) -> re.Pattern[str]:
        """The compiled regex."""
        if self._compiled is None:
            self._compiled = re.compile(self.build_optimized_pattern(), re.VERSION1)
        return self._compiled

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if match := self.pattern.match(state.input, start):
            yield Success(None, match.end())

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 0
        return self

    def update(self, *choices: _Choice) -> LazyChoiceRegex:
        """Update this regex's choices with `choices`."""
        self._choices.extend(choices)
        return self

    def copy(self, *choices: _Choice) -> LazyChoiceRegex:
        """Return a new choice regex with choices from this expression and `choices`."""
        return LazyChoiceRegex(self._choices).update(*choices)

    def build_optimized_pattern(self) -> str:
        """Return a regex pattern matching all collected choices."""
        return build_optimized_pattern(self._choices)


def build_optimized_pattern(choices: list[_Choice]) -> str:  # noqa: PLR0912
    """Return a regex pattern matching any item from `choices`."""
    if not choices:
        return ""

    # Buckets
    char_class_parts = []  # for single-char literals
    ranges = []  # for character ranges
    multi_sensitive = []  # for multi-char sensitive literals
    insensitive_parts = []  # for insensitive literals (scoped flag)
    unicode_props = []  # for UnicodeProperty patterns

    for choice in choices:
        # TODO: structural pattern matching
        if isinstance(choice, UnicodePropertyRule) and isinstance(
            choice.expression, RegexExpression
        ):
            unicode_props.append(choice.expression.pattern)
        elif isinstance(choice, tuple):
            if len(choice) == 2 and isinstance(choice[1], ChoiceCase):
                lit, case = choice
                if case == ChoiceCase.INSENSITIVE:
                    if len(lit) == 1:
                        char_class_parts.append(lit.upper())
                        char_class_parts.append(lit.lower())
                    else:
                        insensitive_parts.append(f"(?i:{re.escape(lit)})")
                elif case == ChoiceCase.SENSITIVE:
                    if len(lit) == 1:
                        char_class_parts.append(lit)
                    else:
                        multi_sensitive.append(re.escape(lit))
            elif len(choice) == 2:  # Range  # noqa: PLR2004
                ranges.append(choice)
            else:
                raise ValueError(f"Unrecognized choice: {choice}")
        else:
            raise ValueError(f"Unrecognized choice type: {choice}")

    parts = []
    if char_class_parts or ranges:
        parts.append(_optimize_char_class(char_class_parts, ranges))
    if multi_sensitive:
        parts.extend(multi_sensitive)
    if insensitive_parts:
        parts.extend(insensitive_parts)
    if unicode_props:
        parts.extend(unicode_props)

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
