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
        passes: list[OptimizerStep],
    ):
        self.passes = passes
        # TODO: Write to logging.debug instead?
        self.log: list[str] = []

    def optimize(
        self, rules: Mapping[str, Rule], *, debug: bool = False
    ) -> Mapping[str, Rule]:
        """Apply optimization passes to all rules."""
        if debug:
            self.log.clear()

        for name, rule in rules.items():
            # TODO: some passes should only be applied to atomic rules
            expr = rule.expression
            for step in self.passes:
                if step.fixed_point:
                    expr = self._run_fixed_point(expr, step, rules, debug=debug)
                else:
                    expr = self._run_once(expr, step, rules, debug=debug)
            rules[name].expression = expr
        return rules

    def _run_once(
        self,
        expr: Expression,
        step: OptimizerStep,
        rules: Mapping[str, Rule],
        *,
        debug: bool,
    ) -> Expression:
        if step.direction == PassDirection.POSTORDER:
            return expr.map_bottom_up(
                lambda e: self._apply(step, e, rules, debug=debug)
            )
        return expr.map_top_down(lambda e: self._apply(step, e, rules, debug=debug))

    def _run_fixed_point(
        self,
        expr: Expression,
        step: OptimizerStep,
        rules: Mapping[str, Rule],
        *,
        debug: bool,
    ) -> Expression:
        max_iters = 20
        for _ in range(max_iters):
            new_expr = self._run_once(expr, step, rules, debug=debug)
            if new_expr is expr:  # No change
                return expr
            expr = new_expr
        raise RuntimeError(
            f"optimizer pass {step.name} did not converge after {max_iters} iterations"
        )

    def _apply(
        self,
        step: OptimizerStep,
        expr: Expression,
        rules: Mapping[str, Rule],
        *,
        debug: bool,
    ) -> Expression:
        new_expr = step.func(expr, rules)
        if debug and new_expr is not expr:
            self.log.append(f"{step.name}: {expr} → {new_expr}")
        return new_expr
