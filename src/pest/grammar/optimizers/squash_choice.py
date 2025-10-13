"""Transform choice of literals into a single regex expression."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Choice
from pest.grammar import CIString
from pest.grammar import Range
from pest.grammar import Rule
from pest.grammar import String
from pest.grammar.expressions.choice import ChoiceCase
from pest.grammar.expressions.choice import ChoiceLiteral
from pest.grammar.expressions.choice import ChoiceRange
from pest.grammar.expressions.choice import LazyChoiceRegex
from pest.grammar.rules.unicode import UnicodePropertyRule

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pest.grammar import Expression


def squash_choice(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    """Transform choice of literals into a single regex expression."""
    if not isinstance(expr, Choice):
        return expr

    exprs = expr.expressions
    return squash(exprs, LazyChoiceRegex()) or expr


def squash(
    exprs: list[Expression],
    new_expr: LazyChoiceRegex,
) -> LazyChoiceRegex | None:
    for expr in exprs:
        if isinstance(expr, String):
            new_expr.update(ChoiceLiteral(expr.value, ChoiceCase.SENSITIVE))
        elif isinstance(expr, CIString):
            new_expr.update(ChoiceLiteral(expr.value, ChoiceCase.INSENSITIVE))
        elif isinstance(expr, UnicodePropertyRule):
            new_expr.update(expr)
        elif isinstance(expr, Range):
            new_expr.update(ChoiceRange(expr.start, expr.stop))
        elif isinstance(expr, Rule) and isinstance(expr.expression, Choice):
            if not squash(expr.expression.expressions, new_expr):
                return None
        elif isinstance(expr, Choice):
            squash(expr.expressions, new_expr)
        elif isinstance(expr, LazyChoiceRegex):
            new_expr.update(*expr._choices)  # noqa: SLF001
        else:
            return None

    return new_expr
