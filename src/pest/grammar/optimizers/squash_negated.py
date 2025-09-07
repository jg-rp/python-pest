"""Replace negated built-in regex rules with a single expression."""

from typing import Mapping

from pest.grammar.expression import Expression
from pest.grammar.expressions.lazy_regex import LazyRegexExpression
from pest.grammar.expressions.prefix import NegativePredicate
from pest.grammar.expressions.rule import BuiltInRegexRangeRule
from pest.grammar.expressions.rule import BuiltInRegexRule
from pest.grammar.expressions.rule import Rule
from pest.grammar.expressions.terminals import Literal


def collapse_negated_builtin(
    expr: Expression, _rules: Mapping[str, Rule]
) -> Expression:
    """Replace negated built-in regex rules with a single expression."""
    if isinstance(expr, NegativePredicate) and isinstance(
        expr.expression, BuiltInRegexRule
    ):
        # TODO: constructor or more convenient method
        regex_expr = LazyRegexExpression()
        regex_expr.negatives.extend(expr.expression.patterns)
        return regex_expr

    if isinstance(expr, NegativePredicate) and isinstance(
        expr.expression, BuiltInRegexRangeRule
    ):
        # TODO: constructor or more convenient method
        regex_expr = LazyRegexExpression()
        regex_expr.negative_ranges.extend(expr.expression.ranges)
        return regex_expr
    return expr


def collapse_negated_literal(
    expr: Expression, _rules: Mapping[str, Rule]
) -> Expression:
    """Replace negated literals with a single expression."""
    if isinstance(expr, NegativePredicate) and isinstance(expr.expression, Literal):
        # TODO: constructor or more convenient method
        regex_expr = LazyRegexExpression()
        regex_expr.negatives.append(expr.expression.value)
        return regex_expr

    # TODO: case insensitive literals - will need to add support in LazyRegexExpression
    return expr


# TODO: squash LazyRegexExpression ~ Any -> LazyRegexExpression
# XXX: Negated regex expressions should not consume anything.
