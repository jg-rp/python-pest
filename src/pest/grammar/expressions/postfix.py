"""pest postfix operators."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest import ParserState
    from pest.result import ParseResult

# TODO: skip if WHITESPACE and/or COMMENT


class Optional(Expression):
    """A optional pest grammar expression.

    This corresponds to the `?` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}?"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Repeat(Expression):
    """A pest grammar expression repeated zero or more times.

    This corresponds to the `*` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}*"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


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

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class RepeatExact(Expression):
    """A pest grammar expression repeated a specified number of times.

    This corresponds to the `{n}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}{{{self.number}}}"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class RepeatMin(Expression):
    """A pest grammar expression repeated at least a specified number of times.

    This corresponds to the `{n,}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}{{{self.number},}}"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class RepeatMax(Expression):
    """A pest grammar expression repeated at most a specified number of times.

    This corresponds to the `{,n}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}{{,{self.number}}}"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class RepeatRange(Expression):
    """A pest grammar expression repeated a specified range of times.

    This corresponds to the `{n,m}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "min",
        "max",
    )

    def __init__(
        self, expression: Expression, min_: int, max_: int, tag: str | None = None
    ):
        super().__init__(tag)
        self.expression = expression
        self.min = min_
        self.max = max_

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}{{{self.min}, {self.max}}}"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
