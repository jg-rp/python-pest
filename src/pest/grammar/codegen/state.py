from typing import Sequence

from pest.stack import Stack


class ParserState:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.user_stack = Stack[str]()  # PUSH/POP/PEEK/DROP
        self.modifier_stack = Stack[int]()  # bit fields
        # TODO: rule stack

    def checkpoint(self) -> None:
        """Mark the current state as a checkpoint."""
        self.user_stack.snapshot()
        self.modifier_stack.snapshot()

    def ok(self) -> None:
        """Discard the last checkpoint after a successful match."""
        self.user_stack.drop_snapshot()
        self.modifier_stack.drop_snapshot()

    def restore(self) -> None:
        """Restore the state to the most recent checkpoint."""
        self.user_stack.restore()
        self.modifier_stack.restore()

    def push(self, value: str) -> None:
        """Push a value onto the stack."""
        self.user_stack.push(value)

    def drop(self) -> None:
        """Pops one item from the top of the stack."""
        self.user_stack.pop()

    def peek(self) -> str | None:
        """Peek at the top element of the stack."""
        return self.user_stack.peek()

    def peek_slice(
        self, start: int | None = None, end: int | None = None
    ) -> Sequence[str]:
        """Peek at a slice of the stack, similar to pest's `PEEK(start..end)`.

        Args:
            start: Start index of the slice (0 = bottom of stack).
            end:   End index of the slice (exclusive).

        Returns:
            A list of values from the stack slice. If no arguments are given,
            return the entire stack.

        Example:
            stack = [1, 2, 3, 4]
            peek_slice()         -> [1, 2, 3, 4]
            peek_slice(0, 2)     -> [1, 2]
            peek_slice(1, 3)     -> [2, 3]
            peek_slice(-2, None) -> [3, 4]
        """
        if start is None and end is None:
            return self.user_stack[:]
        return self.user_stack[slice(start, end)]
