"""Terminal expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

import regex as re

from pest.grammar.expression import Expression
from pest.grammar.expression import Success

if TYPE_CHECKING:
    from pest.state import ParserState


class PushLiteral(Expression):
    """A PUSH terminal with a string literal argument."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f'{self.tag_str()}PUSH("{self.value}")'

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        state.push(self.value)
        yield Success(None, start)


class Push(Expression):
    """A PUSH terminal with an expression."""

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}PUSH( {self.expression} )"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        result = list(self.expression.parse(state, start))
        if not result:
            return

        state.push(state.input[start : result[-1].pos])
        yield from self.filter_silent(result)


class PeekSlice(Expression):
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


class Identifier(Expression):
    """A terminal pointing to rule, possibly a built-in rule."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.value}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        # Assumes the rule exists.
        yield from self.filter_silent(
            state.parser.rules[self.value].parse(state, start)
        )


class Literal(Expression):
    """A terminal string literal."""

    __slots__ = ("value",)

    def __init__(self, value: str):
        super().__init__(None)
        self.value = value
        # TODO: unescape value

    def __str__(self) -> str:
        return f'"{self.value}"'

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        if state.input.startswith(self.value, start):
            yield Success(None, start + len(self.value))


class CaseInsensitiveString(Expression):
    """A terminal string literal that matches case insensitively."""

    __slots__ = ("value", "_re")

    def __init__(self, value: str):
        super().__init__(None)
        # TODO: unescape value
        self.value = value
        self._re = re.compile(re.escape(value), re.I)

    def __str__(self) -> str:
        return f'{self.tag_str()}^"{self.value}"'

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        if self._re.match(state.input, start):
            yield Success(None, start + len(self.value))


class Range(Expression):
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

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        if self._re.match(state.input, start):
            yield Success(None, start + 1)
