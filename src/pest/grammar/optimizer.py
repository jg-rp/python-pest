from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable

from .expression import Expression
from .expressions.choice import Choice
from .expressions.postfix import Optional
from .expressions.postfix import Repeat
from .expressions.sequence import Sequence

Optimizer = Callable[[Expression], Expression]


class OptimizerRegistry:
    """A registry of optimization passes for grammar expressions."""

    def __init__(self, *, debug: bool = False):
        self.passes: list[tuple[str, Optimizer]] = []
        self.debug = debug
        self.log: list[str] = []  # records what was applied

    def register(self, name: str) -> Callable[[Optimizer], Optimizer]:
        """Decorator to register an optimizer by name."""

        def decorator(func: Optimizer) -> Optimizer:
            self.passes.append((name, func))
            return func

        return decorator

    def optimize(self, expr: Expression) -> Expression:
        # Recurse into subexpressions
        if isinstance(expr, Sequence):
            expr = Sequence(
                self.optimize(expr.left),
                self.optimize(expr.right),
            )
        elif isinstance(expr, Choice):
            expr = Choice(
                self.optimize(expr.left),
                self.optimize(expr.right),
            )
        elif isinstance(expr, Repeat):
            expr = Repeat(self.optimize(expr.expression))
        elif isinstance(expr, Optional):
            expr = Optional(self.optimize(expr.expression))

        # TODO: other expression containers

        # Run passes
        for name, opt in self.passes:
            optimized = opt(expr)
            if optimized is not expr:  # changed
                if self.debug:
                    self.log.append(f"{name}: {expr!s}  →  {optimized!s}")
                expr = optimized

        return expr
