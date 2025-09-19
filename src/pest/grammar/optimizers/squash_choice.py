"""Transform choice of literals into a single regex expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Choice
from pest.grammar import CIString
from pest.grammar import RegexExpression
from pest.grammar import Rule
from pest.grammar import Sequence
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
    match expr:
        case Choice(expressions=exprs) if all(
            isinstance(expr, (String, CIString)) for expr in exprs
        ):
            return LazyChoiceRegex(
                [
                    ChoiceLiteral(
                        expr.value,
                        ChoiceCase.SENSITIVE
                        if isinstance(expr, String)
                        else ChoiceCase.INSENSITIVE,
                    )
                    for expr in exprs
                ]
            )
        case _:
            return expr
