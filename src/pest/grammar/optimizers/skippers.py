"""Optimizer passes..."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Choice
from pest.grammar import Group
from pest.grammar import Identifier
from pest.grammar import NegativePredicate
from pest.grammar import Repeat
from pest.grammar import Rule
from pest.grammar import Sequence
from pest.grammar import Skip
from pest.grammar import String
from pest.grammar.rules.special import Any

if TYPE_CHECKING:
    from pest.grammar import Expression


def skip(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """Transform repeated negative predicate ~ ANY into a regex expression."""
    # TODO: only if rule has no inner (is atomic, explicitly or implicitly)
    # TODO: What would this look like with a `match` statement?
    if (
        isinstance(expr, Repeat)
        and isinstance(expr.expression, Group)
        and isinstance(expr.expression.expression, Sequence)
        and len(expr.expression.expression.expressions) == 2  # noqa: PLR2004
    ):
        left, right = expr.expression.expression.expressions

        if isinstance(left, NegativePredicate) and isinstance(right, Any):
            if isinstance(left.expression, Rule):
                new_expr = _skip(left.expression.expression, rules, [])
            else:
                new_expr = _skip(left.expression, rules, [])

            if new_expr:
                return new_expr

    return expr


def _skip(expr: Expression, rules: Mapping[str, Rule], subs: list[str]) -> Skip | None:
    if isinstance(expr, Choice):
        for ex in expr.expressions:
            inlined_subs = _skip(ex, rules, subs)
            if not inlined_subs:
                return None
        return Skip(subs)

    if isinstance(expr, Skip):
        subs.extend(expr.subs)
        return Skip(subs)

    if isinstance(expr, String):
        subs.append(expr.value)
        return Skip(subs)

    if isinstance(expr, Identifier):
        rule = rules.get(expr.value)
        if rule:
            return _skip(rule, rules, subs)

    return None
