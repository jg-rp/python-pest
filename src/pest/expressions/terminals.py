"""Terminal expressions."""

from pest import Expression
from pest import Node
from pest import ParserState
from pest import Token


class PushLiteral(Expression):
    """A PUSH terminal with a string literal argument."""

    __slots__ = ("token",)

    def __init__(self, token: Token):
        self.token = token

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

    def __init__(self, expression: Expression):
        self.expression = expression

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

    def __init__(self, start: Token | None = None, stop: Token | None = None):
        self.start = start
        self.stop = stop

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

    def __init__(self, token: Token):
        self.token = token

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class String(Expression):
    """A terminal string literal."""

    __slots__ = ("token",)

    def __init__(self, token: Token):
        self.token = token

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

    def __init__(self, token: Token):
        self.token = token

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

    def __init__(self, start: Token, stop: Token):
        self.start = start
        self.stop = stop

    def parse(self, state: ParserState, start: int) -> tuple[Node, int] | None:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
