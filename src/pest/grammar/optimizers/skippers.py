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
    # NOTE: The reference implementation only applies "skip" to atomic type rules.
    # As far as I can tell, this is acting like an "early return" as the "ANY" in
    # Rep-NegPred-Any would consume whitespace and comments.

    # TODO: performance implications of `match`/`case`
    match expr:
        case Repeat(expression=Group(expression=Sequence(expressions=[left, right]))):
            match (left, right):
                case (NegativePredicate(expression=inner), Any()) if isinstance(
                    inner, Rule
                ):
                    new_expr = _skip(inner.expression, rules, [])
                    if new_expr:
                        return new_expr

                case (NegativePredicate(expression=inner), Any()):
                    new_expr = _skip(inner, rules, [])
                    if new_expr:
                        return new_expr

        case _:
            return expr

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
