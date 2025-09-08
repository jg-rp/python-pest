"""Replace negated built-in regex rules with a single expression."""

from typing import Mapping

from pest.grammar.expression import Expression
from pest.grammar.expressions.group import Group
from pest.grammar.expressions.lazy_regex import LazyRegexExpression
from pest.grammar.expressions.postfix import Repeat
from pest.grammar.expressions.prefix import NegativePredicate
from pest.grammar.expressions.rule import BuiltInRegexRangeRule
from pest.grammar.expressions.rule import BuiltInRegexRule
from pest.grammar.expressions.rule import Rule
from pest.grammar.expressions.sequence import Sequence
from pest.grammar.rules.special import Any


def collapse_negated_builtin(
    expr: Expression, _rules: Mapping[str, Rule]
) -> Expression:
    """Replace negated built-in regex rules with a single expression."""
    if isinstance(expr, NegativePredicate):
        if isinstance(expr.expression, BuiltInRegexRule):
            return LazyRegexExpression(
                negatives=list(expr.expression.patterns),
                consuming=False,
            )

        if isinstance(expr.expression, BuiltInRegexRangeRule):
            return LazyRegexExpression(
                negative_ranges=list(expr.expression.ranges),
                consuming=False,
            )

    return expr


# TODO: collapse_negated_literal
# TODO: collapse negated groups


def collapse_negated_any(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    """Replace negative predicate followed by ANY with a single regex."""
    if not isinstance(expr, Sequence):
        return expr

    expressions = expr.expressions

    if len(expr.expressions) != 2:
        return expr

    left, right = expressions

    if (
        isinstance(left, LazyRegexExpression)
        and not left.consuming
        and isinstance(right, Any)
    ):
        left.consuming = True
        return left

    return expr


def collapse_group_repeat(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    if (
        isinstance(expr, Repeat)
        and isinstance(expr.expression, Group)
        and isinstance(expr.expression.expression, LazyRegexExpression)
    ):
        return expr.expression.expression.repeat()
    return expr
