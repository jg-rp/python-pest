"""Terminal expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar.expression import Expression

if TYPE_CHECKING:
    from pest.grammar.expression import Success
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
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Push(Expression):
    """A PUSH terminal with an expression."""

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}PUSH( {self.expression} )"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
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
        start: str | None = None,
        stop: str | None = None,
        tag: str | None = None,
    ):
        super().__init__(tag)
        self.start = start
        self.stop = stop

    def __str__(self) -> str:
        start = self.start if self.start else ""
        stop = self.stop if self.stop else ""
        return f"{self.tag_str()}PEEK[{start}..{stop}]"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Identifier(Expression):
    """A terminal pointing to rule, possibly a built-in rule."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.value}"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Literal(Expression):
    """A terminal string literal."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value
        # TODO: unescape value

    def __str__(self) -> str:
        return f'{self.tag_str()}"{self.value}"'

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class CaseInsensitiveString(Expression):
    """A terminal string literal that matches case insensitively."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value
        # TODO: unescape token.value

    def __str__(self) -> str:
        return f'{self.tag_str()}^"{self.value}"'

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:


class Range(Expression):
    """A terminal range of characters."""

    __slots__ = ("start", "stop")

    def __init__(self, start: str, stop: str, tag: str | None = None):
        super().__init__(tag)
        self.start = start
        self.stop = stop
        # TODO: unescape start and stop?

    def __str__(self) -> str:
        return f"{self.tag_str()}'{self.start}'..'{self.stop}'"

    def parse(self, state: ParserState, start: int) -> Iterator[Success]:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        # TODO:
