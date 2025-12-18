"""A stack that supports snapshot and rewind operations.

This is a pretty close translation of the `Stack` struct from Rest pest.

https://github.com/pest-parser/pest/blob/3da954b0034643533e597ae0dffa6e31193af475/pest/src/stack.rs#L17

See LICENSE_PEST.txt
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import islice
from typing import TYPE_CHECKING
from typing import Generic
from typing import Optional
from typing import TypeAlias
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

    def __reversed__(self) -> Iterator[T]:
        return reversed(self.items)

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


_Node: TypeAlias = tuple[T, Optional["_Node[T]"]]


class PersistentStack(Generic[T]):
    """A simplified stack that stores items as persistent nodes."""

    __slots__ = ("_top", "_checkpoints")

    def __init__(self) -> None:
        self._top: _Node[T] | None = None
        self._checkpoints: list[_Node[T] | None] = []

    def empty(self) -> bool:
        """Return `True` if this stack is empty."""
        return self._top is None

    def push(self, item: T) -> None:
        """Push item onto the stack."""
        self._top = (item, self._top)

    def pop(self) -> T:
        """Remove and return the item at the top of the stack."""
        if self._top is None:
            raise IndexError("pop from empty stack")

        value, node = self._top
        self._top = node
        return value

    def peek(self) -> T:
        """Return the item at the top of the stack without removing it."""
        if self._top is None:
            raise IndexError("peek from empty stack")
        return self._top[0]

    def snapshot(self) -> None:
        """Take a snapshot of the stack for later restore."""
        self._checkpoints.append(self._top)

    def restore(self) -> None:
        """Rewind the stack to the most recent snapshot."""
        if not self._checkpoints:
            self._top = None
            return

        self._top = self._checkpoints.pop()

    def drop_snapshot(self) -> None:
        """Drop the last snapshot."""
        if self._checkpoints:
            self._checkpoints.pop()

    def clear(self) -> None:
        """Remove all items from the stack."""
        self._top = None

    def __iter__(self) -> Iterator[T]:
        values: list[T] = []
        current = self._top
        while current is not None:
            values.append(current[0])
            current = current[1]
        return iter(reversed(values))

    def __reversed__(self) -> Iterator[T]:
        current = self._top
        while current is not None:
            yield current[0]
            current = current[1]

    def copy(self) -> PersistentStack[T]:
        """Return a copy of the stack without checkpoints."""
        s = PersistentStack[T]()
        s.push(self.peek())
        return s


BLOCK_SIZE = 32


class Block(Generic[T]):
    __slots__ = ("items", "prev_block", "cumulative_count")

    def __init__(self, items: tuple[T, ...], prev_block: Optional[Block[T]] = None):
        self.items = items
        self.prev_block = prev_block
        # Stores total items in all blocks up to and including this one
        prev_count = prev_block.cumulative_count if prev_block else 0
        self.cumulative_count = prev_count + len(items)


class PersistentSequenceStack(Sequence[T], Generic[T]):
    def __init__(self) -> None:
        self._head_block: Optional[Block[T]] = None
        self._buffer: list[T] = []
        # Checkpoints store (head_block, buffer_contents_tuple)
        self._checkpoints: list[tuple[Optional[Block[T]], tuple[T, ...]]] = []

    def push(self, item: T) -> None:
        if len(self._buffer) >= BLOCK_SIZE:
            self._head_block = Block(tuple(self._buffer), self._head_block)
            self._buffer = []
        self._buffer.append(item)

    def pop(self) -> T:
        if not self._buffer:
            if not self._head_block:
                raise IndexError("pop from empty stack")
            # Move the top immutable block back into the mutable buffer
            self._buffer = list(self._head_block.items)
            self._head_block = self._head_block.prev_block
        return self._buffer.pop()

    def snapshot(self) -> None:
        """O(1) Snapshot: Capture the current state."""
        self._checkpoints.append((self._head_block, tuple(self._buffer)))

    def restore(self) -> None:
        """O(1) Restore: Revert to the last snapshot state."""
        if not self._checkpoints:
            self._head_block = None
            self._buffer = []
        else:
            self._head_block, buffer_tuple = self._checkpoints.pop()
            self._buffer = list(buffer_tuple)

    def empty(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        block_count = self._head_block.cumulative_count if self._head_block else 0
        return block_count + len(self._buffer)

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    def __getitem__(self, index: int | slice) -> T | Sequence[T]:
        if isinstance(index, slice):
            # For simplicity, convert to list for slicing,
            # or implement a lazy view for better performance.
            return list(self)[index]

        length = len(self)
        if index < 0:
            index += length
        if index < 0 or index >= length:
            raise IndexError("index out of range")

        # Check if the index is in the current mutable buffer
        block_offset = self._head_block.cumulative_count if self._head_block else 0
        if index >= block_offset:
            return self._buffer[index - block_offset]

        # Otherwise, traverse the immutable blocks
        curr = self._head_block
        while curr:
            start_of_block = curr.cumulative_count - len(curr.items)
            if index >= start_of_block:
                return curr.items[index - start_of_block]
            curr = curr.prev_block
        raise IndexError

    def __iter__(self) -> Iterator[T]:
        # Collect blocks to iterate forward without recursion
        blocks = []
        curr = self._head_block
        while curr:
            blocks.append(curr)
            curr = curr.prev_block

        # Yield from oldest block to newest
        for block in reversed(blocks):
            yield from block.items

        # Finally yield from the active buffer
        yield from self._buffer

    def __reversed__(self) -> Iterator[T]:
        yield from reversed(self._buffer)
        curr = self._head_block
        while curr:
            yield from reversed(curr.items)
            curr = curr.prev_block

    def drop_snapshot(self) -> None:
        """Drop the most recent snapshot without restoring state."""
        if self._checkpoints:
            self._checkpoints.pop()

    def clear(self) -> None:
        """Remove all existing snapshots."""
        self._checkpoints.clear()

    def peek(self) -> T:
        """Return the top item without removing it."""
        if self._buffer:
            return self._buffer[-1]
        if self._head_block:
            return self._head_block.items[-1]
        raise IndexError("peek from empty stack")

    def copy(self) -> PersistentSequenceStack[T]:
        stack = PersistentSequenceStack[T]()
        stack._head_block = self._head_block
        stack._buffer = list(self._buffer)
        return stack


class UndoStack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
        self._ptr: int = 0  # Points to the NEXT available slot
        self._snapshots: list[int] = []

    def push(self, item: T) -> None:
        if self._ptr < len(self._items):
            self._items[self._ptr] = item
        else:
            self._items.append(item)
        self._ptr += 1

    def pop(self) -> T:
        if self._ptr == 0:
            raise IndexError
        self._ptr -= 1
        return self._items[self._ptr]

    def peek(self) -> T:
        if self._ptr == 0:
            raise IndexError
        return self._items[self._ptr - 1]

    def snapshot(self) -> None:
        self._snapshots.append(self._ptr)

    def restore(self) -> None:
        self._ptr = self._snapshots.pop() if self._snapshots else 0

    def __len__(self) -> int:
        return self._ptr

    def empty(self) -> bool:
        return self._ptr != 0

    def drop_snapshot(self) -> None:
        self._snapshots.pop()

    def copy(self) -> UndoStack:
        stack = UndoStack()
        stack._items = self._items[: self._ptr]
        return stack

    def __iter__(self) -> Iterator[T]:
        return islice(self._items, self._ptr)
