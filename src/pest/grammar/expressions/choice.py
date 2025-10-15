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
from pest.grammar.expression import RegexExpression
from pest.grammar.rules.unicode import UnicodePropertyRule

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.pairs import Pair
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

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:
        """Attempt to match this expression against the input at `start`."""
        for expr in self.expressions:
            state.checkpoint()
            children: list[Pair] = []
            matched = expr.parse(state, children)

            if matched:
                state.ok()
                pairs.extend(children)
                return True

            state.restore()
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a choice expression (A | B | ...).

        Each branch is attempted in order until one succeeds.
        On success, the matched branch's pairs are appended to `pairs_var`.
        On failure, parser state is restored to the checkpoint taken before
        that branch began.
        """
        gen.writeln("# <Choice>")

        # Temporary list to collect results from each branch.
        # This ensures that pairs produced by a failed branch do not leak.
        tmp_pairs = gen.new_temp("children")

        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln(f"{matched_var} = False")

        # Generate code for each alternative in order.
        for branch in self.expressions:
            # Only attempt another branch if none have succeeded yet.
            gen.writeln(f"if not {matched_var}:")
            with gen.block():
                # Take a checkpoint so we can backtrack if this branch fails.
                gen.writeln("state.checkpoint()")

                # Generate code for the branch itself.
                branch.generate(gen, matched_var, tmp_pairs)

                # If the branch matched, commit and extend parent pairs.
                gen.writeln(f"if {matched_var}:")
                with gen.block():
                    gen.writeln("state.ok()")
                    gen.writeln(f"{pairs_var}.extend({tmp_pairs})")

                # Otherwise, revert to the pre-branch state and clear partial results.
                gen.writeln("else:")
                with gen.block():
                    gen.writeln("state.restore()")
                    gen.writeln(f"{tmp_pairs}.clear()")

        gen.writeln("# </Choice>")

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


class OptimizedChoice(Expression):
    """An optimized expression for matching a set of choices using a single regex.

    Supports single-character literals, multi-character literals (case-sensitive or
    insensitive), character ranges, and Unicode property rules.

    Args:
        choices: Optional initial list of choices to match.
    """

    __slots__ = ("choices", "_compiled")

    def __init__(self, choices: list[ChoiceChoice] | None = None):
        super().__init__(None)
        self.choices = choices or []
        self._compiled: re.Pattern[str] | None = None

    def __str__(self) -> str:
        return f"/{self.pattern.pattern!r}/"

    @property
    def pattern(self) -> re.Pattern[str]:
        """The compiled regex."""
        if self._compiled is None:
            self._compiled = re.compile(self.build_optimized_pattern(), re.VERSION1)
        return self._compiled

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: ARG002
        """Attempt to match this expression against the input at `start`."""
        if match := self.pattern.match(state.input, state.pos):
            state.pos = match.end()
            return True
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:  # noqa: ARG002
        """Emit Python code for an optimized regex choice expression."""
        gen.writeln("# <ChoiceRegex>")

        pattern = self.build_optimized_pattern()
        re_var = gen.constant("RE", f"re.compile({pattern!r}, re.VERSION1)")

        gen.writeln(f"if match := {re_var}.match(state.input, state.pos):")
        with gen.block():
            gen.writeln("state.pos = match.end()")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")

        gen.writeln("# </ChoiceRegex>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 0
        return self

    def update(self, *choices: ChoiceChoice) -> OptimizedChoice:
        """Add choices to this regex and return self."""
        self.choices.extend(choices)
        return self

    def copy(self, *choices: ChoiceChoice) -> OptimizedChoice:
        """Return a new LazyChoiceRegex with current and additional choices."""
        return OptimizedChoice(self.choices).update(*choices)

    def build_optimized_pattern(self) -> str:
        """Return a regex pattern matching all collected choices."""
        return build_optimized_pattern(self.choices)


class OptimizedChoiceRepeat(OptimizedChoice):
    """An optimized `("a" | "b")*`."""

    def build_optimized_pattern(self) -> str:
        """Return a regex pattern matching all collected choices."""
        return build_optimized_pattern(self.choices, "*")


def build_optimized_pattern(choices: list[ChoiceChoice], repeat: str = "") -> str:  # noqa: PLR0912
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

    parts: list[str] = []
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
        if repeat:
            return f"(?:{parts[0]}){repeat}"
        return parts[0]
    return "(?:" + "|".join(parts) + ")" + repeat


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
