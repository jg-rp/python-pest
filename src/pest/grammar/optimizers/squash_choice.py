"""Transform choice of literals into a single regex expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping
from typing import TypeGuard

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
    from pest.grammar import Expression


def squash_choice(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    """Transform choice of literals into a single regex expression."""
    if not isinstance(expr, Choice):
        return expr

    exprs = expr.expressions
    if _squashable(exprs):
        return _squash(exprs, LazyChoiceRegex()) or expr
    return expr


def _squashable(
    choices: list[Expression],
) -> TypeGuard[list[String | CIString | Range | Rule]]:
    return all(isinstance(e, (String, CIString | Range | Rule)) for e in choices)


def _squash(
    exprs: list[String | CIString | Range | Rule], new_expr: LazyChoiceRegex
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
        elif (
            isinstance(expr, Rule)
            and isinstance(expr.expression, Choice)
            and _squashable(expr.expression.expressions)
        ):
            if not _squash(expr.expression.expressions, new_expr):
                return None
        else:
            return None

    return new_expr
