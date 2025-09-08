"""Replace identifiers with the rule they point to."""

from typing import Mapping

from pest.grammar.expression import Expression
from pest.grammar.expressions.rule import GrammarRule
from pest.grammar.expressions.rule import Rule
from pest.grammar.expressions.terminals import Identifier


def inline_identifiers(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """Replace identifiers with the rules they point to."""
    if not isinstance(expr, Identifier):
        return expr

    rule = rules.get(expr.value)

    if isinstance(rule, GrammarRule):
        if rule.modifier == "_":
            # The rule is silent. We can inline the rule's expression.
            return rule.expression
        return rule

    return expr
