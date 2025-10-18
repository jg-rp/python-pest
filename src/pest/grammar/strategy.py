"""Hypothesis strategy context."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Mapping

    from .rule import Rule


class StrategyContext:
    """Hypothesis strategy generation state."""

    def __init__(
        self,
        rules: Mapping[str, Rule],
        recursion_depth: int = 0,
        atomic_depth: int = 0,
        max_recursion: int = 10,
    ) -> None:
        self.rules = rules
        self.rule_depth = recursion_depth
        self.atomic_depth = atomic_depth
        self.max_recursion = max_recursion

    @contextmanager
    def descend(self, *, atomic: bool = False) -> Iterator["StrategyContext"]:
        """Temporarily increment recursion and optionally atomic depth."""
        if self.rule_depth >= self.max_recursion:
            raise RecursionError(
                "exceeded maximum recursion depth in strategy generation"
            )

        self.rule_depth += 1
        if atomic:
            self.atomic_depth += 1

        try:
            yield self
        finally:
            # Restore depths
            self.rule_depth -= 1
            if atomic:
                self.atomic_depth -= 1
