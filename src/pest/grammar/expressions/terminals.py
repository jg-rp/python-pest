"""Terminal expressions."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING
from typing import Iterator
from typing import Self

import regex as re

from pest.grammar.expression import Expression
from pest.grammar.expression import Success
from pest.grammar.expression import Terminal

if TYPE_CHECKING:
    from pest.grammar.rule import Rule
    from pest.state import ParserState


class PushLiteral(Terminal):
    """A PUSH terminal with a string literal argument."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f'{self.tag_str()}PUSH("{self.value}")'

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        state.push(self.value)
        yield Success(None, start)

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


# TODO: PUSH(expression) is not terminal


class Push(Expression):
    """A PUSH terminal with an expression."""

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}PUSH( {self.expression} )"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        result = list(state.parse(self.expression, start, self.tag))
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

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class PeekSlice(Terminal):
    """A PEEK terminal with a range expression.

    Matches the range from the bottom of the stack to the top.
    """

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
        """Attempt to match this expression against the input at `start`."""
        position = start

        for literal in state.peek_slice(self.start, self.stop):
            if state.input.startswith(literal, position):
                position += len(literal)
            else:
                return

        # TODO: If the end lies before or at the start, the expression matches
        # (as does a PEEK_ALL on an empty stack).
        yield Success(None, position)

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class Peek(Terminal):
    """A PEEK terminal looking at the top of the stack."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}PEEK"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        with suppress(IndexError):
            value = state.stack.peek()
            if state.input.startswith(value, start):
                yield Success(None, start + len(value))

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class PeekAll(Terminal):
    """A PEEK_ALL terminal match the entire stack, top to bottom."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}PEEK_ALL"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        position = start
        stack_size = len(state.stack)

        for i, literal in enumerate(reversed(state.stack)):
            # XXX: can `literal` be empty?
            if not state.input.startswith(literal, position):
                return

            position += len(literal)

            if i < stack_size:
                implicit_result = list(state.parse_implicit_rules(position))
                if implicit_result:
                    position = implicit_result[-1].pos

        yield Success(None, position)

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class Pop(Terminal):
    """A POP terminal popping off the top of the stack."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}POP"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        with suppress(IndexError):
            value = state.stack.peek()
            if state.input.startswith(value, start):
                state.stack.pop()
                yield Success(None, start + len(value))

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class PopAll(Terminal):
    """A POP_ALL terminal matching the entire stack, top to bottom."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}POP_ALL"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        position = start
        state.snapshot()

        while not state.stack.empty():
            literal = state.stack.pop()
            if not state.input.startswith(literal, position):
                state.restore()
                return

            position += len(literal)

            # TODO: don't skip trivia after the last pop
            if implicit_result := list(state.parse_implicit_rules(position)):
                position = implicit_result[-1].pos

        yield Success(None, position)

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class Drop(Terminal):
    """A DROP terminal that matches if the stack is not empty."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}DROP"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if not state.stack.empty():
            state.stack.pop()
            yield Success(None, start)

    def is_pure(self, _rules: dict[str, Rule], _seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class Identifier(Terminal):
    """A terminal pointing to rule, possibly a built-in rule."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.value}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Identifier) and other.value == self.value

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        # TODO: Assumes the rule exists.
        yield from state.parse(state.parser.rules[self.value], start, self.tag)

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        seen = seen or set()
        if self.value not in seen and self._pure is None:
            seen.add(self.value)
            self._pure = rules[self.value].is_pure(rules, seen)
        return self._pure or False


class String(Terminal):
    """A terminal string literal."""

    __slots__ = ("value",)

    def __init__(self, value: str):
        super().__init__(None)
        self.value = value

    def __str__(self) -> str:
        # TODO: replace non-printing characters with \u{XXXX} escape sequence
        value = (
            self.value.replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")
        )
        return f'"{value}"'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, String) and self.value == other.value

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if state.input.startswith(self.value, start):
            yield Success(None, start + len(self.value))


class CIString(Terminal):
    """A terminal string literal that matches case insensitively."""

    __slots__ = ("value", "_re")

    def __init__(self, value: str):
        super().__init__(None)
        # TODO: unescape value
        self.value = value
        self._re = re.compile(re.escape(value), re.I)

    def __str__(self) -> str:
        # TODO: replace non-printing characters with \u{XXXX} escape sequence
        value = (
            self.value.replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")
        )
        return f'{self.tag_str()}^"{value}"'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CIString) and self.value == other.value

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
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

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`."""
        if match := self._re.match(state.input, start):
            yield Success(None, match.end())


class SkipUntil(Terminal):
    """A terminal that matches characters until one of a set of substrings is found.

    Attributes:
        subs: The list of substrings that terminate the match.
    """

    __slots__ = ("subs",)

    def __init__(self, subs: list[str]):
        super().__init__(tag=None)
        self.subs = subs

    def __str__(self) -> str:
        _subs = [repr(s)[1:-1] for s in self.subs]
        strings = " | ".join(f'"{s}"' for s in _subs)
        return f"(!({strings}) ~ ANY)*"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SkipUntil) and other.subs == self.subs

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        The match consumes characters until the earliest occurrence of any of
        the substrings in `self.subs`.

        Notes:
            - Benchmarks show this simple "loop and find" implementation to be
              faster than an Aho-Corasick approach up to a couple hundred
              substrings (`len(self.subs)`).
        """
        best_index: int | None = None
        s = state.input

        for sub in self.subs:
            pos = s.find(sub, start)
            if pos != -1 and (best_index is None or pos < best_index):
                best_index = pos

        if best_index is not None:
            yield Success(None, best_index)
        else:
            yield Success(None, len(s))
