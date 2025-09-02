"""pest postfix operators."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

from pest.grammar import Expression
from pest.grammar.expression import Success

if TYPE_CHECKING:
    from pest import ParserState


class Optional(Expression):
    """A optional pest grammar expression.

    This corresponds to the `?` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        super().__init__(None)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.expression}?"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        result = next(self.expression.parse(state, start), None)
        if result:
            yield result
        else:
            yield Success(None, start)


class Repeat(Expression):
    """A pest grammar expression repeated zero or more times.

    This corresponds to the `*` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        super().__init__(None)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.expression}*"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        position = start
        while True:
            result = next(self.expression.parse(state, position), None)
            if not result:
                break
            position = result.pos
            yield result

            for success in state.parse_implicit_rules(position):
                position = success.pos
                if success.node:
                    yield success

        # Always succeed.
        # TODO: or a flag, in case previous successes don't consume anything.
        if position != start:
            yield Success(None, start)


class RepeatOnce(Expression):
    """A pest grammar expression repeated one or more times.

    This corresponds to the `+` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}+"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        result = next(self.expression.parse(state, start), None)

        if not result:
            return

        yield result

        position = result.pos

        for success in state.parse_implicit_rules(position):
            position = success.pos
            if success.node:
                yield success

        while True:
            result = next(self.expression.parse(state, position), None)
            if not result:
                break
            position = result.pos
            yield result

            for success in state.parse_implicit_rules(position):
                position = success.pos
                if success.node:
                    yield success


class RepeatExact(Expression):
    """A pest grammar expression repeated a specified number of times.

    This corresponds to the `{n}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int):
        super().__init__(None)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.expression}{{{self.number}}}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        successes: list[Success] = []
        position = start

        while True:
            result = next(self.expression.parse(state, position), None)
            if not result:
                break
            position = result.pos
            successes.append(result)

            for success in state.parse_implicit_rules(position):
                position = success.pos
                successes.append(result)

        if len(successes) == self.number:
            yield from self.filter_silent(successes)


class RepeatMin(Expression):
    """A pest grammar expression repeated at least a specified number of times.

    This corresponds to the `{n,}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int):
        super().__init__(None)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.expression}{{{self.number},}}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        successes: list[Success] = []
        position = start

        while True:
            result = next(self.expression.parse(state, position), None)
            if not result:
                break
            position = result.pos
            successes.append(result)

            for success in state.parse_implicit_rules(position):
                position = success.pos
                successes.append(result)

        if len(successes) >= self.number:
            yield from self.filter_silent(successes)


class RepeatMax(Expression):
    """A pest grammar expression repeated at most a specified number of times.

    This corresponds to the `{,n}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int):
        super().__init__(None)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.expression}{{,{self.number}}}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        successes: list[Success] = []
        position = start

        while True:
            result = next(self.expression.parse(state, position), None)
            if not result:
                break
            position = result.pos
            successes.append(result)

            for success in state.parse_implicit_rules(position):
                position = success.pos
                successes.append(result)

        if len(successes) <= self.number:
            yield from self.filter_silent(successes)


class RepeatRange(Expression):
    """A pest grammar expression repeated a specified range of times.

    This corresponds to the `{n,m}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "min",
        "max",
    )

    def __init__(self, expression: Expression, min_: int, max_: int):
        super().__init__(None)
        self.expression = expression
        self.min = min_
        self.max = max_

    def __str__(self) -> str:
        return f"{self.expression}{{{self.min}, {self.max}}}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`."""
        successes: list[Success] = []
        position = start

        while True:
            result = next(self.expression.parse(state, position), None)
            if not result:
                break
            position = result.pos
            successes.append(result)

            for success in state.parse_implicit_rules(position):
                position = success.pos
                successes.append(result)

        if len(successes) >= self.min and len(successes) <= self.max:
            yield from self.filter_silent(successes)
