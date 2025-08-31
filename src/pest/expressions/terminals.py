"""Terminal expressions."""

from pest import Expression
from pest import Node
from pest import ParserState
from pest import Token


class PushLiteral(Expression):
    """A PUSH terminal with a string literal argument."""

    __slots__ = ("token",)

    def __init__(self, token: Token, tag: Token | None = None):
        super().__init__(tag)
        self.token = token

    def __str__(self) -> str:
        # TODO: tag
        return f'PUSH("{self.token.value}")'

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Push(Expression):
    """A PUSH terminal with an expression."""

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: Token | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        # TODO: tag
        return f"PUSH( {self.expression} )"

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class PeekSlice(Expression):
    """A PEEK terminal with a range expression."""

    __slots__ = ("start", "stop")

    def __init__(
        self,
        start: Token | None = None,
        stop: Token | None = None,
        tag: Token | None = None,
    ):
        super().__init__(tag)
        self.start = start
        self.stop = stop

    def __str__(self) -> str:
        # TODO: tag
        start = self.start.value if self.start else ""
        stop = self.stop.value if self.stop else ""
        return f"PEEK[{start}..{stop}]"

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Identifier(Expression):
    """A terminal pointing to rule, possibly a built-in rule."""

    __slots__ = ("token",)

    def __init__(self, token: Token, tag: Token | None = None):
        super().__init__(tag)
        self.token = token

    def __str__(self) -> str:
        # TODO: tag
        return self.token.value

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Literal(Expression):
    """A terminal string literal."""

    __slots__ = ("token",)

    def __init__(self, token: Token, tag: Token | None = None):
        super().__init__(tag)
        self.token = token
        # TODO: unescape token.value

    def __str__(self) -> str:
        # TODO: tag
        return f'"{self.token.value}"'

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class CaseInsensitiveString(Expression):
    """A terminal string literal that matches case insensitively."""

    __slots__ = ("token",)

    def __init__(self, token: Token, tag: Token | None = None):
        super().__init__(tag)
        self.token = token
        # TODO: unescape token.value

    def __str__(self) -> str:
        # TODO: tag
        return f'^"{self.token.value}"'

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Range(Expression):
    """A terminal range of characters."""

    __slots__ = ("start", "stop")

    def __init__(self, start: Token, stop: Token, tag: Token | None = None):
        super().__init__(tag)
        self.start = start
        self.stop = stop
        # TODO: unescape start and stop?

    def __str__(self) -> str:
        # TODO: tag
        return f"'{self.start.value}'..'{self.stop.value}'"

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
