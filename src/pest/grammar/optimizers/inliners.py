"""Optimizer passes that inline rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Identifier
from pest.grammar.rule import SILENT
from pest.grammar.rule import BuiltInRule

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pest.grammar import Expression
    from pest.grammar import Rule


def inline_builtin(expr: Expression, rules: Mapping[str, Rule]) -> Expression:  # noqa: ARG001
    """Inline built-in rules.

    Inline rules are always silent so we can replace Identifier with the rule's
    inner expression.
    """
    if isinstance(expr, BuiltInRule) and expr.name != "EOI":
        return expr.expression
    return expr


def inline_silent_rules(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """Inline silent rules."""
    if isinstance(expr, Identifier):
        rule = rules[expr.value]
        if rule.modifier & SILENT:
            return rule.expression
    return expr
