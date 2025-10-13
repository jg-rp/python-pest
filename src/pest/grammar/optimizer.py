"""A registry of optimization passes for grammar expressions."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import MutableMapping
from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import TypeAlias

from pest.grammar import Choice
from pest.grammar import Repeat
from pest.grammar import Rule
from pest.grammar.expressions import OptimizedChoiceRepeat
from pest.grammar.rule import SILENT
from pest.grammar.rule import SILENT_ATOMIC

from .expression import Expression
from .optimizers.inliners import inline_builtin
from .optimizers.inliners import inline_silent_rules
from .optimizers.skippers import skip
from .optimizers.squash_choice import squash
from .optimizers.squash_choice import squash_choice
from .optimizers.unroller import unroll

OptimizerPass: TypeAlias = Callable[[Expression, Mapping[str, Rule]], Expression]
OptimizerPassPredicate: TypeAlias = Callable[[Mapping[str, Rule]], bool]


class PassDirection(Enum):
    """Optimizer tree traversal order."""

    PREORDER = auto()
    POSTORDER = auto()


@dataclass
class OptimizerStep:
    """An optimizer pass with associated traversal direction.

    Arguments:
        name: A label for the optimizer step used in the log.
        func: A callable that implements the optimizer pass.
        direction: Perform optimization passes from bottom to top (post order)
            or top to bottom (pre order).
        fixed_point: If True`, repeat the pass until it fails to perform any
            optimizations.
        predicate: If not `None`, the predicate is called with the rules to
            be optimized as its only argument. The step will be skipped if the
            predicate returns `False`.

    """

    name: str
    func: Callable[[Expression, Mapping[str, Rule]], Expression]
    direction: PassDirection
    fixed_point: bool = False
    predicate: OptimizerPassPredicate | None = None


DEFAULT_OPTIMIZER_PASSES = [
    OptimizerStep("unroll", unroll, PassDirection.POSTORDER),
    OptimizerStep("skip", skip, PassDirection.PREORDER),
    OptimizerStep("inline built-in", inline_builtin, PassDirection.PREORDER),
    OptimizerStep("squash_choice", squash_choice, PassDirection.POSTORDER),
    OptimizerStep("inline silent", inline_silent_rules, PassDirection.POSTORDER),
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

        assert isinstance(rules, dict)
        self._optimize_skip_rule(rules)

        for step in self.passes:
            if step.predicate and not step.predicate(rules):
                continue

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
        # NOTE: COMMENT and WHITESPACE are hard coded to always be atomic.

        comment = rules.get("COMMENT")
        whitespace = rules.get("WHITESPACE")

        if comment and whitespace:
            # TODO:
            return

        if comment and comment.modifier & SILENT:
            rules["SKIP"] = Rule("SKIP", Repeat(comment.expression), SILENT_ATOMIC)

        elif (
            whitespace
            and whitespace.modifier & SILENT
            and isinstance(whitespace.expression, Choice)
        ):
            expr = squash(whitespace.expression.expressions, OptimizedChoiceRepeat())
            if expr:
                rules["SKIP"] = Rule("SKIP", expr, SILENT_ATOMIC)

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
