"""WHITESPACE optimizer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Choice
from pest.grammar import Rule
from pest.grammar import Sequence
from pest.grammar.expressions.choice import LazyChoiceRegex

if TYPE_CHECKING:
    from pest.grammar import Expression


def inline_whitespace(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """"""
    ws = rules.get("WHITESPACE")
    if not ws or not isinstance(ws.expression, LazyChoiceRegex):
        return expr

    # TODO: Silent and atomic bit mask?
    # TODO: this is a special pass that does not fit into OptimizerStep
    # TODO:
