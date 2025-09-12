from pest.stack import Stack


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


# TODO: snapshot_pop_restore
