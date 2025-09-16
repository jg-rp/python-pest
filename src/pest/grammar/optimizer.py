"""A registry of optimization passes for grammar expressions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Callable
from typing import Mapping

from pest.grammar.expressions import Rule

from .expression import Expression

OptimizerPass = Callable[[Expression, Mapping[str, Rule]], Expression]


class PassDirection(Enum):
    """Optimizer tree traversal order."""

    PREORDER = auto()
    POSTORDER = auto()


@dataclass
class OptimizerStep:
    """An optimizer pass with associated traversal direction."""

    name: str
    func: Callable[[Expression, Mapping[str, Rule]], Expression]
    direction: PassDirection
    fixed_point: bool = False


class Optimizer:
    """A pest AST optimizer."""

    def __init__(
        self,
        rules: Mapping[str, Rule],
        passes: list[OptimizerStep],
        *,
        debug: bool = False,
    ):
        self.rules = rules
        self.passes = passes
        self.debug = debug
        self.log: list[str] = []

    def optimize(self, expr: Expression) -> Expression:
        """Apply optimization passes to `expr`."""
        for step in self.passes:
            if step.fixed_point:
                expr = self._run_fixed_point(expr, step)
            else:
                expr = self._run_once(expr, step)
        return expr

    def _run_once(self, expr: Expression, step: OptimizerStep) -> Expression:
        if step.direction == PassDirection.POSTORDER:
            return expr.map_bottom_up(lambda e: self._apply(step, e))
        return expr.map_top_down(lambda e: self._apply(step, e))

    def _run_fixed_point(self, expr: Expression, step: OptimizerStep) -> Expression:
        max_iters = 20
        for _ in range(max_iters):
            new_expr = self._run_once(expr, step)
            if new_expr is expr:  # No change
                return expr
            expr = new_expr
        raise RuntimeError(
            f"optimizer pass {step.name} did not converge after {max_iters} iterations"
        )

    def _apply(self, step: OptimizerStep, expr: Expression) -> Expression:
        new_expr = step.func(expr, self.rules)
        if new_expr is not expr and self.debug:
            self.log.append(f"{step.name}: {expr} → {new_expr}")
        return new_expr
