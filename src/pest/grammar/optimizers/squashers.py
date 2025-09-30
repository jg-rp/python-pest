"""Optimizer passes that squash expression."""

from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Choice
from pest.grammar import Repeat
from pest.grammar import Sequence
from pest.grammar.expression import Terminal
from pest.grammar.expressions.choice import LazyChoiceRegex
from pest.grammar.rule import SILENT
from pest.grammar.rule import BuiltInRule

if TYPE_CHECKING:
    from pest.grammar import Expression
    from pest.grammar import Rule

# TODO:
# def search(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
#     """Squash consecutive choice expressions."""
#     if isinstance(expr, Repeat) and isinstance(expr.expression, Terminal):
#         print("**", expr)

#     if isinstance(expr, Sequence):
#         for a, b in pairwise(expr.expressions):
#             if isinstance(a, Choice) and isinstance(b, Choice):
#                 print("FOUND!", a, b)
#             if isinstance(a, LazyChoiceRegex) and isinstance(b, LazyChoiceRegex):
#                 print("FOUND!", a, b)

#     return expr
