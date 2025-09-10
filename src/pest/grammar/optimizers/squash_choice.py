"""Replace identifiers with the rule they point to."""

from typing import Mapping

import regex as re

from pest.grammar.expression import Expression
from pest.grammar.expressions.choice import Choice
from pest.grammar.expressions.lazy_regex import LazyRegexExpression
from pest.grammar.expressions.rule import BuiltInRegexRule
from pest.grammar.expressions.rule import GrammarRule
from pest.grammar.expressions.rule import Rule
from pest.grammar.expressions.terminals import Identifier
from pest.grammar.expressions.terminals import String

# TODO: case insensitive literal
# TODO: char range
# TODO: built-in char range


# TODO: negated literals to regex before this


def squash_choice(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    """Replace literal and regex choices with a single regex."""
    if not isinstance(expr, Choice) or not all(
        isinstance(e, (String, LazyRegexExpression, BuiltInRegexRule))
        for e in expr.expressions
    ):
        return expr

    regex = LazyRegexExpression()

    for ex in expr.expressions:
        if isinstance(ex, String):
            # if len(ex.value) == 1:
            #     regex.positive_ranges.append((re.escape(ex.value), re.escape(ex.value)))
            # else:
            regex.positives.append(re.escape(ex.value))
        elif isinstance(ex, BuiltInRegexRule):
            regex.positives.extend(ex.patterns)
        # TODO: LazyRegexExpression

    return regex
