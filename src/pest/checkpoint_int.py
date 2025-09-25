"""An integer that supports checkpoint and restore operations."""

from __future__ import annotations

from typing_extensions import Self


class SnapshottingInt:
    """An integer that supports checkpoint and restore operations."""

    def __init__(self, value: int = 0) -> None:
        self._value: int = value
        self._checkpoints: list[int] = []

    def snapshot(self) -> None:
        """Save the current value onto the checkpoint stack."""
        self._checkpoints.append(self._value)

    def restore(self) -> Self:
        """Restore to the last checkpoint.

        If no checkpoints exist, restore to initial state (0).
        """
        if self._checkpoints:
            self._value = self._checkpoints.pop()
        else:
            self._value = 0
        return self

    def drop(self) -> None:
        """Drop the last checkpoint."""
        if self._checkpoints:
            self._checkpoints.pop()

    def zero(self) -> None:
        """Set the current value to `0`."""
        self._value = 0

    def __int__(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return f"CheckpointInt({self._value})"

    def __str__(self) -> str:
        return str(self._value)

    def __add__(self, other: int | SnapshottingInt) -> Self:
        self._value += int(other)
        return self

    def __sub__(self, other: int | SnapshottingInt) -> Self:
        self._value -= int(other)
        return self

    def __mul__(self, other: int | SnapshottingInt) -> Self:
        self._value *= int(other)
        return self

    def __floordiv__(self, other: int | SnapshottingInt) -> Self:
        self._value //= int(other)
        return self

    def __truediv__(self, other: int | SnapshottingInt) -> Self:
        self._value = int(self._value / int(other))
        return self

    def __mod__(self, other: int | SnapshottingInt) -> Self:
        self._value %= int(other)
        return self

    def __pow__(self, other: int | SnapshottingInt) -> Self:
        self._value **= int(other)
        return self

    def __neg__(self) -> Self:
        self._value = -self._value
        return self

    def __pos__(self) -> Self:
        self._value = +self._value
        return self

    def __abs__(self) -> Self:
        self._value = abs(self._value)
        return self

    def __eq__(self, value: object) -> bool:
        return isinstance(value, int) and self._value == int(value)

    def __ne__(self, value: object) -> bool:
        return isinstance(value, int) and self._value != int(value)

    def __lt__(self, value: object) -> bool:
        return isinstance(value, int) and self._value < int(value)

    def __le__(self, value: object) -> bool:
        return isinstance(value, int) and self._value <= int(value)

    def __gt__(self, value: object) -> bool:
        return isinstance(value, int) and self._value > int(value)

    def __ge__(self, value: object) -> bool:
        return isinstance(value, int) and self._value >= int(value)
