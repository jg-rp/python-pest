"""Optimizer passes that inline rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar.expressions.rule import BuiltInRule

if TYPE_CHECKING:
    from pest.grammar import Expression
    from pest.grammar import Rule


def inline_builtin(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    """Inline built-in rules.

    Inline rules are always silent so we can replace Identifier with the rule's
    inner expression.
    """
    if isinstance(expr, BuiltInRule):
        return expr.expression
    return expr
