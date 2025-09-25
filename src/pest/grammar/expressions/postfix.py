"""pest postfix operators."""

from __future__ import annotations

from typing import TYPE_CHECKING
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

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        matches = state.parse(self.expression, start, self.tag)
        if matches:
            return matches
        return [Match(None, start)]

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

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        position = start
        matched = False
        matches = []

        while True:
            state.snapshot()
            results = state.parse(self.expression, position, self.tag)

            if not results:
                state.restore()
                break

            matched = True
            position = results[-1].pos
            state.ok()
            matches.extend(results)

            for match in state.parse_implicit_rules(position):
                position = match.pos
                matches.append(match)

        # Always succeed.
        if not matched:
            return [Match(None, position)]
        return matches

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

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        state.snapshot()
        matches = state.parse(self.expression, start, self.tag)

        if not matches:
            state.restore()
            return None

        state.ok()
        position = matches[-1].pos

        for success in state.parse_implicit_rules(position):
            position = success.pos
            matches.append(success)

        while True:
            state.snapshot()
            results = state.parse(self.expression, position, self.tag)
            if not results:
                state.restore()
                break
            position = results[-1].pos
            state.ok()
            matches.extend(results)

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        return matches

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

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = state.parse(self.expression, position, self.tag)

            if not results:
                break

            position = results[-1].pos
            matches.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        if match_count == self.number:
            state.ok()
            return matches

        state.restore()
        return None

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

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = state.parse(self.expression, position, self.tag)
            if not results:
                break
            position = results[-1].pos
            matches.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        if match_count >= self.number:
            state.ok()
            return matches

        state.restore()
        return None

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

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        position = start
        state.snapshot()

        for i in range(self.number):
            results = state.parse(self.expression, position, self.tag)
            if not results:
                break

            position = results[-1].pos
            matches.extend(results)

            if i < self.number - 1:
                for success in state.parse_implicit_rules(position):
                    position = success.pos
                    matches.append(success)

        if matches:
            state.ok()
            return matches

        state.restore()
        return None

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

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = state.parse(self.expression, position, self.tag)
            if not results:
                break
            position = results[-1].pos
            matches.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        if match_count >= self.min and match_count <= self.max:
            state.ok()
            return matches

        state.restore()
        return None

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.min, self.max)
