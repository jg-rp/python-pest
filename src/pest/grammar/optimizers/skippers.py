"""Optimizer passes..."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Identifier
from pest.grammar import NegativePredicate
from pest.grammar import Repeat
from pest.grammar import Rule
from pest.grammar import Sequence

if TYPE_CHECKING:
    from pest.grammar import Expression

# TODO: rename me.
# Rust pest calls this "skip", and has a `Skip` variant in its AST.


def skip(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """Transform repeated negative predicate ~ ANY into a regex expression."""
    # TODO: only if rule has no inner (is atomic, explicitly or implicitly)
    if (
        isinstance(expr, Repeat)
        and isinstance(expr.expression, Sequence)
        and len(expr.expression.expressions) == 2  # noqa: PLR2004
    ):
        left, right = expr.expression.expressions
        if (
            isinstance(left, NegativePredicate)
            and isinstance(right, Identifier)
            and right.value == "ANY"
        ):
            new_expr = _neg_pred_any_regex_expression(left.expression, rules)
            if new_expr:
                return new_expr

    return expr


# XXX: Do we need a `Skip` expression to later turn into a regex expression?


def _neg_pred_any_regex_expression(
    expr: Expression, rules: Mapping[str, Rule]
) -> Expression | None:
    raise NotImplementedError
