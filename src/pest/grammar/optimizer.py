"""A registry of optimization passes for grammar expressions."""

from __future__ import annotations

from typing import Callable
from typing import Mapping

from pest.grammar.expressions import Rule

from .expression import Expression

OptimizerPass = Callable[[Expression, Mapping[str, Rule]], Expression]


class Optimizer:
    """A registry of optimization passes for grammar expressions."""

    def __init__(
        self,
        rules: Mapping[str, Rule],
        passes: list[tuple[str, OptimizerPass]],
        *,
        debug: bool = False,
    ):
        self.rules = rules
        self.passes = passes
        self.debug = debug
        self.log: list[str] = []

    def optimize(self, expr: Expression) -> Expression:
        """Return an optimized version of `expr`."""
        # Recursively optimize children
        new_children = [self.optimize(c) for c in expr.children()]
        if new_children != expr.children():
            expr = expr.with_children(new_children)

        # Apply optimization passes
        for name, opt in self.passes:
            new_expr = opt(expr, self.rules)
            if new_expr is not expr:
                if self.debug:
                    self.log.append(f"{name}: {expr} → {new_expr}")
                expr = new_expr

        return expr
