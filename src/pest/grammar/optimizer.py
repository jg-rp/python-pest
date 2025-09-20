"""A registry of optimization passes for grammar expressions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Callable
from typing import Mapping
from typing import MutableMapping

from pest.grammar import Choice
from pest.grammar import Repeat
from pest.grammar import Rule
from pest.grammar.expressions.rule import BuiltInRule

from .expression import Expression
from .optimizers.inliners import inline_builtin
from .optimizers.skippers import skip
from .optimizers.squash_choice import squash_choice
from .optimizers.unroller import unroll

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


DEFAULT_OPTIMIZER_PASSES = [
    OptimizerStep("skip", skip, PassDirection.PREORDER),
    OptimizerStep("inline built-in", inline_builtin, PassDirection.PREORDER),
    OptimizerStep("unroll", unroll, PassDirection.POSTORDER),
    OptimizerStep("squash_choice", squash_choice, PassDirection.POSTORDER),
]


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

        for step in self.passes:
            for name, rule in rules.items():
                # TODO: some passes should only be applied to atomic rules
                expr = rule.expression

                if step.fixed_point:
                    expr = self._run_fixed_point(expr, step, rules, name, debug=debug)
                else:
                    expr = self._run_once(expr, step, rules, name, debug=debug)
                rules[name].expression = expr

        return rules

    def _optimize_skip_rule(self, rules: MutableMapping[str, Rule]) -> None:
        """Combine WHITESPACE and COMMENT into a single SKIP rule."""
        comment = rules.get("COMMENT")
        whitespace = rules.get("WHITESPACE")

        if comment and whitespace:
            rules["SKIP"] = BuiltInRule(
                "SKIP",
                Repeat(Choice(whitespace.expression, comment.expression)),
                "$",
            )
        elif comment:
            rules["SKIP"] = BuiltInRule("SKIP", Repeat(comment.expression), "$")
        elif whitespace:
            rules["SKIP"] = BuiltInRule("SKIP", Repeat(whitespace.expression), "_")

    def _run_once(
        self,
        expr: Expression,
        step: OptimizerStep,
        rules: Mapping[str, Rule],
        start_rule_name: str,
        *,
        debug: bool,
    ) -> Expression:
        if step.direction == PassDirection.POSTORDER:
            return expr.map_bottom_up(
                lambda e: self._apply(step, e, rules, start_rule_name, debug=debug)
            )
        return expr.map_top_down(
            lambda e: self._apply(step, e, rules, start_rule_name, debug=debug)
        )

    def _run_fixed_point(
        self,
        expr: Expression,
        step: OptimizerStep,
        rules: Mapping[str, Rule],
        start_rule_name: str,
        *,
        debug: bool,
    ) -> Expression:
        max_iters = 20
        for _ in range(max_iters):
            new_expr = self._run_once(expr, step, rules, start_rule_name, debug=debug)
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
        start_rule_name: str,
        *,
        debug: bool,
    ) -> Expression:
        new_expr = step.func(expr, rules)
        if debug and new_expr is not expr:
            self.log.append(f"{step.name}({start_rule_name}): {expr} → {new_expr}")
        return new_expr


DEFAULT_OPTIMIZER = Optimizer(DEFAULT_OPTIMIZER_PASSES)
