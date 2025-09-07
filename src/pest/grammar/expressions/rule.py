"""A logical grammar rule."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterable
from typing import Iterator

import regex as re
from typing_extensions import Self

from pest.grammar import Expression
from pest.grammar.expression import Success
from pest.pairs import Pair

if TYPE_CHECKING:
    from pest.state import ParserState


class Rule(Expression):
    """Base class for all rules."""

    __slots__ = ("name", "modifier", "doc")

    def __init__(
        self,
        name: str,
        modifier: str | None = None,
        doc: Iterable[str] | None = None,
    ):
        super().__init__(tag=None)
        self.name = name
        self.modifier = modifier
        self.doc = tuple(doc) if doc else None

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.modifier == other.modifier
            and self.doc == other.doc
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.modifier, self.doc, self.tag))


class GrammarRule(Rule):
    """A named grammar rule."""

    __slots__ = ("expression",)

    def __init__(
        self,
        name: str,
        expression: Expression,
        modifier: str | None = None,
        doc: Iterable[str] | None = None,
    ):
        super().__init__(name, modifier, doc)
        self.expression = expression

    def __str__(self) -> str:
        doc = "".join(f"///{line}\n" for line in self.doc) if self.doc else ""
        modifier = self.modifier if self.modifier else ""
        return f"{doc}{self.name} = {modifier}{{ {self.expression} }}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.expression == other.expression
            and self.modifier == other.modifier
            and self.doc == other.doc
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash(
            (self.__class__, self.expression, self.modifier, self.doc, self.tag)
        )

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state.
            start: The index in the input string where parsing begins.
        """
        restore_atomic_depth = state.atomic_depth

        if self.modifier in ("@", "$"):
            state.atomic_depth += 1
        elif self.modifier == "!":
            state.atomic_depth = 0

        results = list(state.parse(self.expression, start))

        if not results:
            state.atomic_depth = restore_atomic_depth
            return

        end = results[-1].pos

        if self.modifier == "_":
            # Yield children without an enclosing Pair
            yield from results
        elif self.modifier == "@":
            # Atomic rule silences children
            yield Success(
                Pair(
                    input_=state.input,
                    rule=self,
                    start=start,
                    end=end,
                    children=[],
                ),
                pos=end,
            )
        else:
            yield Success(
                Pair(
                    input_=state.input,
                    rule=self,
                    start=start,
                    end=end,
                    children=[success.pair for success in results if success.pair],
                ),
                pos=end,
            )

        # Restore atomic depth to what it was before this rule
        state.atomic_depth = restore_atomic_depth

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(self.name, expressions[0], self.modifier, self.doc)


class BuiltInRule(Rule):
    """The base class for all built-in rules."""

    def children(self) -> list[Expression]:
        """Return this expressions children."""
        return []

    def with_children(self, _expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self


class BuiltInRegexRule(BuiltInRule):
    """A built-in rule based on a regular expression."""

    __slots__ = ("_re", "patterns")

    def __init__(self, name: str, *patterns: str):
        super().__init__(name, "_", None)
        self.patterns = patterns
        self._re = re.compile("|".join(patterns))

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BuiltInRegexRule) and self.patterns == other.patterns

    def __hash__(self) -> int:
        return hash((self.__class__, self.name, self._re.pattern))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if match := self._re.match(state.input, start):
            yield Success(None, match.end())


class BuiltInRegexRangeRule(BuiltInRule):
    """A built-in rule based on a range of characters."""

    __slots__ = ("_re", "ranges")

    def __init__(self, name: str, *ranges: tuple[str, str]):
        super().__init__(name, "_", None)
        self.ranges = ranges
        _ranges = "".join(
            f"{re.escape(start)}-{re.escape(end)}" for start, end in ranges
        )
        self._re = re.compile(f"[{_ranges}]")

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BuiltInRegexRangeRule) and self.ranges == other.ranges

    def __hash__(self) -> int:
        return hash((self.__class__, self.name, self.ranges))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if match := self._re.match(state.input, start):
            yield Success(None, match.end())
