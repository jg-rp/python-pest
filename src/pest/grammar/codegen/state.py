"""Parser state management for running generated parsers.

This module defines the `ParserState` class, which encapsulates the mutable state
used when executing a parser generated from a grammar. It provides stack-based
mechanisms for tracking user values and modifiers, as well as checkpointing and
restoration for backtracking and error recovery.
"""

from typing import Sequence

from pest.stack import Stack


class ParserState:
    """Encapsulates the mutable state of a parser when running generated code.

    The `ParserState` tracks the input text, current position, and multiple stacks
    for user values and modifiers. It supports checkpointing, restoration, and
    stack operations to facilitate backtracking and complex parsing logic during
    the execution of generated parsers.
    """

    def __init__(self, text: str):
        """Initialize a new parser state for the given input text.

        Args:
            text: The input string to be parsed.
        """
        self.text = text
        self.pos = 0
        self.user_stack = Stack[str]()  # PUSH/POP/PEEK/DROP
        self.modifier_stack = Stack[int]()  # bit fields
        # TODO: rule stack

    def checkpoint(self) -> None:
        """Take a snapshot of the current state for potential backtracking.

        Saves the current state of all stacks, allowing restoration if parsing fails.
        """
        self.user_stack.snapshot()
        self.modifier_stack.snapshot()

    def ok(self) -> None:
        """Commit to the current state after a successful parse.

        Discards the last checkpoint, making the changes since the last checkpoint permanent.
        """
        self.user_stack.drop_snapshot()
        self.modifier_stack.drop_snapshot()

    def restore(self) -> None:
        """Restore the state to the most recent checkpoint.

        Reverts all stacks to their state at the last checkpoint, undoing any changes since then.
        """
        self.user_stack.restore()
        self.modifier_stack.restore()

    def push(self, value: str) -> None:
        """Push a value onto the user stack.

        Args:
            value: The value to push onto the stack.
        """
        self.user_stack.push(value)

    def drop(self) -> None:
        """Pop one item from the top of the user stack."""
        self.user_stack.pop()

    def peek(self) -> str | None:
        """Return the value at the top of the user stack, or None if empty."""
        return self.user_stack.peek()

    def peek_slice(
        self, start: int | None = None, end: int | None = None
    ) -> Sequence[str]:
        """Peek at a slice of the user stack, similar to pest's `PEEK(start..end)`.

        Args:
            start: Start index of the slice (0 = bottom of stack).
            end:   End index of the slice (exclusive).

        Returns:
            A list of values from the stack slice. If no arguments are given,
            returns the entire stack.

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
