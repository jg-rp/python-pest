"""Replace negated built-in regex rules with a single expression."""

from pest.grammar.expression import Expression
from pest.grammar.expressions.prefix import NegativePredicate
from pest.grammar.expressions.rule import BuiltInRegexRule


def collapse_negated_builtin(expr: Expression) -> Expression:
    """Replace negated built-in regex rules with a single expression."""
    # XXX: It's not a BuiltInRegexRule, it's an identifier pointing to a built-in
    if isinstance(expr, NegativePredicate) and isinstance(
        expr.expression, BuiltInRegexRule
    ):
        return expr.expression.negated()
    return expr
