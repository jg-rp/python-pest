from enum import IntFlag
import timeit

# Constants
CARRY = 1 << 0
ZERO = 1 << 1


def test_constants(n=10_000):
    flags = 0
    for _ in range(n):
        flags |= CARRY
        flags &= ~ZERO
        if flags & CARRY:
            pass


# IntFlag
class Status(IntFlag):
    CARRY = 1 << 0
    ZERO = 1 << 1


def test_enum(n=10_000):
    flags = Status(0)
    for _ in range(n):
        flags |= Status.CARRY
        flags &= ~Status.ZERO
        if Status.CARRY in flags:
            pass


print(timeit.timeit(test_constants, number=100))  # ~0.02s
print(timeit.timeit(test_enum, number=100))  # ~0.08s
