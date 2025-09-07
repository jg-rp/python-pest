"""Replace negated built-in regex rules with a single expression."""

from typing import Mapping

from pest.grammar.expression import Expression
from pest.grammar.expressions.prefix import NegativePredicate
from pest.grammar.expressions.rule import BuiltInRegexRule
from pest.grammar.expressions.rule import Rule
from pest.grammar.expressions.terminals import CaseInsensitiveString
from pest.grammar.expressions.terminals import Literal


def collapse_negated_builtin(
    expr: Expression, _rules: Mapping[str, Rule]
) -> Expression:
    """Replace negated built-in regex rules with a single expression."""
    if isinstance(expr, NegativePredicate) and isinstance(
        expr.expression, BuiltInRegexRule
    ):
        # TODO: turn these into lazy regex expressions
        return expr.expression.negated()
    return expr


def collapse_negated_literal(
    expr: Expression, _rules: Mapping[str, Rule]
) -> Expression:
    """Replace negated literals with a single expression."""
    if isinstance(expr, NegativePredicate) and isinstance(
        expr.expression, (Literal, CaseInsensitiveString)
    ):
        # TODO: turn these into lazy regex expressions
        return expr.expression.negated()
    return expr
