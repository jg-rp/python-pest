from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Callable

# TODO: store reference to the Grammar instance so we can lookup rules.


@dataclass
class ParserState:
    """Holds parsing state.

    Includes input string, current parsing context, and a stack for stateful
    grammar operations.
    """

    input: str
    atomic_depth: int = 0
    stack: list[object] = field(default_factory=list)

    def skip(
        self,
        pos: int,
        whitespace: Callable[[str, int], int] | None = None,
        comment: Callable[[str, int], int] | None = None,
    ) -> int:
        """Advance past whitespace/comments unless in atomic mode."""
        if self.atomic_depth > 0:
            return pos

        # TODO: get whitespace and/or comment rule from grammar

        while True:
            new_pos = pos
            if whitespace:
                new_pos = whitespace(self.input, new_pos)
            if comment:
                new_pos = comment(self.input, new_pos)
            if new_pos == pos:
                break
            pos = new_pos
        return pos

    def push(self, value: object) -> None:
        """Push a value onto the parsing stack."""
        self.stack.append(value)

    # TODO: PEEK takes slice start and stop indexes

    def peek(self) -> object:
        """Return the top value of the parsing stack without removing it."""
        if not self.stack:
            raise IndexError("PEEK on empty parsing stack")
        return self.stack[-1]

    def drop(self) -> object:
        """Pop and return the top value of the parsing stack."""
        if not self.stack:
            raise IndexError("DROP on empty parsing stack")
        return self.stack.pop()
