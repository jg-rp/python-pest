import pytest

from pest.stack import Stack

# Many of these tests are translated from the Rust implementation.
#
# https://github.com/pest-parser/pest/blob/3da954b0034643533e597ae0dffa6e31193af475/pest/src/stack.rs
#
# See LICENSE_PEST.txt


def test_snapshot_empty_stack() -> None:
    s: Stack[int] = Stack()
    s.snapshot()
    assert s.empty()
    s.push(0)
    s.restore()
    assert s.empty()


def test_snapshot_twice() -> None:
    s: Stack[int] = Stack()
    s.push(0)
    s.snapshot()
    s.snapshot()
    s.restore()
    s.restore()
    assert list(s) == [0]


def test_restore_without_snapshot() -> None:
    s: Stack[int] = Stack()
    s.push(0)
    s.restore()
    assert list(s) == []


def test_snapshot_and_restore() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    s.push(2)
    s.snapshot()  # snapshot [1, 2]
    s.push(3)
    s.push(4)
    s.restore()  # back to [1, 2]
    assert list(s) == [1, 2]


def test_restore_without_snapshot_clears_stack() -> None:
    s: Stack[int] = Stack()
    s.push(10)
    s.push(20)
    s.restore()  # no snapshots, should clear
    assert s.empty()


def test_multiple_snapshots() -> None:
    s: Stack[str] = Stack()
    s.push("a")
    s.snapshot()  # snapshot [a]
    s.push("b")
    s.snapshot()  # snapshot [a, b]
    s.push("c")

    s.restore()  # back to [a, b]
    assert list(s) == ["a", "b"]
    s.restore()  # back to [a]
    assert list(s) == ["a"]


def test_drop_snapshot_discards_last_snapshot() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    s.snapshot()
    s.push(2)
    s.snapshot()
    s.push(3)

    s.drop_snapshot()  # drop second snapshot
    s.restore()  # restore to first snapshot
    assert list(s) == [1]


def test_interleaved_push_pop_with_snapshots() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    s.push(2)
    s.snapshot()  # [1, 2]
    s.push(3)
    s.pop()  # pops 3
    s.push(4)
    s.restore()  # back to [1, 2]
    assert list(s) == [1, 2]


def test_snapshot_pop_restore() -> None:
    s: Stack[int] = Stack()
    s.push(0)
    s.snapshot()
    s.pop()
    s.restore()
    assert list(s) == [0]


def test_snapshot_pop_push_restore() -> None:
    s: Stack[int] = Stack()
    s.push(0)
    s.snapshot()
    s.pop()
    s.push(1)
    s.restore()
    assert list(s) == [0]


def test_snapshot_push_pop_restore() -> None:
    s: Stack[int] = Stack()
    s.push(0)
    s.snapshot()
    s.push(1)
    s.push(2)
    s.pop()
    s.restore()
    assert list(s) == [0]


def test_snapshot_push_drop() -> None:
    s: Stack[int] = Stack()
    s.push(0)
    s.snapshot()
    s.push(1)
    s.drop_snapshot()
    assert list(s) == [0, 1]


def test_snapshot_pop_drop() -> None:
    s: Stack[int] = Stack()
    s.push(0)
    s.push(1)
    s.snapshot()
    s.pop()
    s.drop_snapshot()
    assert list(s) == [0]


def test_stack_ops() -> None:
    s: Stack[int] = Stack()

    # []
    assert s.empty()
    with pytest.raises(IndexError):
        s.peek()
    with pytest.raises(IndexError):
        s.pop()

    # [0]
    s.push(0)
    assert not s.empty()
    assert s.peek() == 0

    # [1]
    s.push(1)
    assert not s.empty()
    assert s.peek() == 1

    # [0]
    assert s.pop() == 1
    assert s.peek() == 0

    # [0, 2]
    s.push(2)
    assert not s.empty()
    assert s.peek() == 2

    # [0, 2, 3]
    s.push(3)
    assert not s.empty()
    assert s.peek() == 3

    # [0, 2, 3]
    s.snapshot()

    # [0, 2]
    assert s.pop() == 3
    assert not s.empty()
    assert s.peek() == 2

    # [0, 2]
    s.snapshot()

    # [0]
    assert s.pop() == 2
    assert not s.empty()
    assert s.peek() == 0

    # []
    assert s.pop() == 0
    assert s.empty()

    # [0, 2]
    s.restore()
    assert s.pop() == 2
    assert s.pop() == 0
    with pytest.raises(IndexError):
        s.pop()

    # [0, 2, 3]
    s.restore()
    assert s.pop() == 3
    assert s.pop() == 2
    assert s.pop() == 0
    with pytest.raises(IndexError):
        s.pop()


def test_clear_no_snapshot() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    s.push(2)
    s.push(3)

    s.clear()

    assert list(s) == []  # items cleared
    assert s.empty()
    assert s.popped == []  # no snapshots => popped list cleared
    assert s.lengths == []  # no snapshots => lengths cleared


def test_clear_with_snapshot_restore() -> None:
    s: Stack[int] = Stack()
    s.push(10)
    s.push(20)
    s.snapshot()
    s.push(30)
    s.push(40)

    s.clear()  # should empty items, but keep snapshot state

    assert list(s) == []  # stack cleared
    assert s.lengths, "snapshot state should be preserved"
    assert len(s.popped) > 0, "popped should hold removed items"

    s.restore()  # restore to snapshot

    # Only the items that existed at snapshot should remain
    assert list(s) == [10, 20]
    assert s.lengths == []  # restore pops snapshot
