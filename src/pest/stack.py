"""A stack that supports snapshot and rewind operations.

This is a pretty close translation of the `Stack` struct from Rest pest.

https://github.com/pest-parser/pest/blob/3da954b0034643533e597ae0dffa6e31193af475/pest/src/stack.rs#L17

See LICENSE_PEST.txt
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import overload

if TYPE_CHECKING:
    from collections.abc import Iterator


T = TypeVar("T")


class Stack(Sequence[T]):
    """A stack that supports snapshot and rewind operations."""

    def __init__(self) -> None:
        self.items: list[T] = []
        self.popped: list[T] = []
        self.lengths: list[tuple[int, int]] = []

    def empty(self) -> bool:
        """Return `True` if this stack is empty."""
        return not self.items

    def peek(self) -> T:
        """Return the item at the top of the stack without removing it.

        Raises an IndexError if the stack is empty.
        """
        return self.items[-1]

    def push(self, item: T) -> None:
        """Push `item` onto the stack."""
        self.items.append(item)

    def pop(self) -> T:
        """Pop an item from the top of the stack.

        Raises an IndexError if the stack is empty.
        """
        size = len(self.items)
        popped = self.items.pop()
        if self.lengths:
            item_count, remained_count = self.lengths[-1]
            if size == remained_count:
                self.lengths[-1] = (item_count, remained_count - 1)
                self.popped.append(popped)
        return popped

    def clear(self) -> None:
        """Remove all items from the stack, preserving snapshot state for restore()."""
        if not self.items:
            return

        removed = self.items[:]
        self.items.clear()

        if self.lengths:
            item_count, _ = self.lengths[-1]
            # Mark all items as popped for the latest snapshot
            self.lengths[-1] = (item_count, 0)
            self.popped.extend(reversed(removed))
        else:
            # No snapshots to restore from; reset everything
            self.popped.clear()
            self.lengths.clear()

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    def __getitem__(self, index: int | slice) -> T | Sequence[T]:
        return self.items[index]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def snapshot(self) -> None:
        """Take a snapshot of the current stack."""
        self.lengths.append((len(self.items), len(self.items)))

    def drop_snapshot(self) -> None:
        """Drop the last snapshot."""
        if self.lengths:
            item_count, remained_count = self.lengths.pop()
            del self.popped[item_count - remained_count :]

    def restore(self) -> None:
        """Rewind the stack to the most recent snapshot.

        If there is no snapshot, empty the stack.
        """
        if not self.lengths:
            self.items.clear()
            assert not self.popped
            assert not self.lengths
            return

        item_count, remained_count = self.lengths.pop()

        if remained_count < len(self.items):
            del self.items[remained_count:]

        if item_count > remained_count:
            rewind_count = item_count - remained_count
            new_size = len(self.popped) - rewind_count
            recovered = self.popped[new_size:]
            del self.popped[new_size:]
            self.items.extend(reversed(recovered))
            assert len(self.popped) == new_size
