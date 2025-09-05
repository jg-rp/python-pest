"""Terminal expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

import regex as re
from typing_extensions import Self

from pest.grammar.expression import Expression
from pest.grammar.expression import Success
from pest.grammar.expression import Terminal

if TYPE_CHECKING:
    from pest.state import ParserState


class PushLiteral(Terminal):
    """A PUSH terminal with a string literal argument."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f'{self.tag_str()}PUSH("{self.value}")'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.value == other.value
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.value, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        state.push(self.value)
        yield Success(None, start)


# TODO: PUSH(expression) is not terminal


class Push(Expression):
    """A PUSH terminal with an expression."""

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}PUSH( {self.expression} )"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.expression == other.expression
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.expression, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        result = list(state.parse(self.expression, start))
        if not result:
            return

        state.push(state.input[start : result[-1].pos])
        yield from result

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)


class PeekSlice(Terminal):
    """A PEEK terminal with a range expression."""

    __slots__ = ("start", "stop")

    def __init__(
        self,
        start: str | None = None,
        stop: str | None = None,
        tag: str | None = None,
    ):
        super().__init__(tag)
        self.start = int(start) if start else None
        self.stop = int(stop) if stop else None

    def __str__(self) -> str:
        start = self.start if self.start else ""
        stop = self.stop if self.stop else ""
        return f"{self.tag_str()}PEEK[{start}..{stop}]"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.start == other.start
            and self.stop == other.stop
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.start, self.stop, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        position = start

        for literal in state.peek_slice(self.start, self.stop):
            if state.input.startswith(literal, position):
                position += len(literal)
            else:
                return

        # TODO: If the end lies before or at the start, the expression matches
        # (as does a PEEK_ALL on an empty stack).
        yield Success(None, position)


class Identifier(Terminal):
    """A terminal pointing to rule, possibly a built-in rule."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.value}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.value == other.value
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.value, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        # TODO: Assumes the rule exists.
        yield from state.parse(state.parser.rules[self.value], start)


class Literal(Terminal):
    """A terminal string literal."""

    __slots__ = ("value",)

    def __init__(self, value: str):
        super().__init__(None)
        self.value = value

    def __str__(self) -> str:
        value = (
            self.value.replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")
        )
        return f'"{value}"'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.value == other.value
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.value, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        if state.input.startswith(self.value, start):
            yield Success(None, start + len(self.value))


class CaseInsensitiveString(Terminal):
    """A terminal string literal that matches case insensitively."""

    __slots__ = ("value", "_re")

    def __init__(self, value: str):
        super().__init__(None)
        # TODO: unescape value
        self.value = value
        self._re = re.compile(re.escape(value), re.I)

    def __str__(self) -> str:
        return f'{self.tag_str()}^"{self.value}"'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.value == other.value
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.value, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        if self._re.match(state.input, start):
            yield Success(None, start + len(self.value))


class Range(Terminal):
    """A terminal range of characters."""

    __slots__ = ("start", "stop", "_re")

    def __init__(self, start: str, stop: str, tag: str | None = None):
        super().__init__(tag)
        self.start = start
        self.stop = stop
        # TODO: unescape start and stop?
        self._re = re.compile(rf"[{re.escape(self.start)}-{re.escape(self.stop)}]")

    def __str__(self) -> str:
        return f"{self.tag_str()}'{self.start}'..'{self.stop}'"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.start == other.start
            and self.stop == other.stop
            and self.tag == other.tag
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self.start, self.stop, self.tag))

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        if self._re.match(state.input, start):
            yield Success(None, start + 1)
