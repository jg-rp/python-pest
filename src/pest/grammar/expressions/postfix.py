"""pest postfix operators."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator
from typing import Self

from pest.grammar import Expression
from pest.grammar.expression import Match

if TYPE_CHECKING:
    from pest.state import ParserState


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

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Optional) and self.expression == other.expression

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        results = list(state.parse(self.expression, start, self.tag))
        if results:
            yield from results
        else:
            yield Match(None, start)

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)


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

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Repeat) and self.expression == other.expression

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Attempt to match this expression against the input at `start`."""
        position = start
        matched = False

        while True:
            state.snapshot()
            results = list(state.parse(self.expression, position, self.tag))

            if not results:
                state.restore()
                break

            matched = True
            position = results[-1].pos
            state.ok()
            yield from results

            for success in state.parse_implicit_rules(position):
                position = success.pos
                yield success

        # Always succeed.
        if not matched:
            yield Match(None, position)

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)


class RepeatOnce(Expression):
    """A pest grammar expression repeated one or more times.

    This corresponds to the `+` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        super().__init__(None)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}+"

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Attempt to match this expression against the input at `start`."""
        state.snapshot()
        results = list(state.parse(self.expression, start, self.tag))

        if not results:
            state.restore()
            return

        state.ok()
        yield from results

        position = results[-1].pos

        for success in state.parse_implicit_rules(position):
            position = success.pos
            yield success

        while True:
            state.snapshot()
            results = list(state.parse(self.expression, position, self.tag))
            if not results:
                state.restore()
                break
            position = results[-1].pos
            state.ok()
            yield from results

            for success in state.parse_implicit_rules(position):
                position = success.pos
                yield success

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)


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

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Attempt to match this expression against the input at `start`."""
        successes: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = list(state.parse(self.expression, position, self.tag))

            if not results:
                break

            position = results[-1].pos
            successes.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                successes.append(success)

        if match_count == self.number:
            state.ok()
            yield from successes
        else:
            state.restore()

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.number)


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

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Attempt to match this expression against the input at `start`."""
        successes: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = list(state.parse(self.expression, position, self.tag))
            if not results:
                break
            position = results[-1].pos
            successes.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                successes.append(success)

        if match_count >= self.number:
            state.ok()
            yield from successes
        else:
            state.restore()

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.number)


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

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Attempt to match this expression against the input at `start`."""
        successes: list[Match] = []
        position = start
        state.snapshot()

        for i in range(self.number):
            results = list(state.parse(self.expression, position, self.tag))
            if not results:
                break

            position = results[-1].pos
            successes.extend(results)

            if i < self.number - 1:
                for success in state.parse_implicit_rules(position):
                    position = success.pos
                    successes.append(success)

        if successes:
            state.ok()
            yield from successes
        else:
            state.restore()

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.number)


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

    def parse(self, state: ParserState, start: int) -> Iterator[Match]:
        """Attempt to match this expression against the input at `start`."""
        successes: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = list(state.parse(self.expression, position, self.tag))
            if not results:
                break
            position = results[-1].pos
            successes.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                successes.append(success)

        if match_count >= self.min and match_count <= self.max:
            state.ok()
            yield from successes
        else:
            state.restore()

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.min, self.max)
