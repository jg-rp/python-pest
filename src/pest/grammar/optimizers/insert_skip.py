"""Insert explicit skip expressions around sequence operators."""

from itertools import chain
from itertools import islice
from itertools import repeat
from typing import Mapping

import regex as re

from pest.grammar.expression import Expression
from pest.grammar.expressions.choice import Choice
from pest.grammar.expressions.lazy_regex import LazyRegexExpression
from pest.grammar.expressions.postfix import Repeat
from pest.grammar.expressions.rule import GrammarRule
from pest.grammar.expressions.rule import Rule
from pest.grammar.expressions.sequence import Sequence


def insert_whitespace(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """Insert explicit whitespace expressions around sequence operators.

    This pass should only be used on COMMENT. Use insert_skip for all other expressions.
    """
    whitespace = rules.get("WHITESPACE")

    if not whitespace or not isinstance(expr, Sequence):
        return expr

    ws = whitespace.expression if isinstance(whitespace, GrammarRule) else whitespace

    if isinstance(ws, LazyRegexExpression):
        ws = ws.repeat()

    expressions = islice(
        chain.from_iterable(zip(repeat(ws), expr.expressions)), 1, None
    )

    expr.expressions = list(expressions)
    return expr


def skip_rule(rules: Mapping[str, Rule]) -> GrammarRule | None:
    """Return rules with WHITESPACE and COMMENT optimized into SKIP."""
    ws = rules.get("WHITESPACE")
    cm = rules.get("COMMENT")

    if ws and cm:
        assert isinstance(ws, GrammarRule)
        assert isinstance(ws.expression, LazyRegexExpression)
        assert isinstance(cm, GrammarRule)

        skip_expr = Repeat(Choice(ws.expression.repeat(), cm.expression))
    elif ws:
        assert isinstance(ws, GrammarRule)
        assert isinstance(ws.expression, LazyRegexExpression)
        skip_expr = Repeat(ws.expression)
    elif cm:
        assert isinstance(cm, GrammarRule)
        skip_expr = Repeat(cm.expression)
    else:
        return None  # no skip rules defined

    return GrammarRule("SKIP", skip_expr, "_")


def insert_skip(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """Insert skip expressions around sequence operators."""
    skip = rules.get("SKIP")

    if not skip or not isinstance(expr, Sequence):
        return expr

    assert isinstance(skip, GrammarRule)

    expressions = islice(
        chain.from_iterable(zip(repeat(skip.expression), expr.expressions)), 1, None
    )

    # XXX: this does not show up in the optimizer log!
    expr.expressions = list(expressions)
    return expr
