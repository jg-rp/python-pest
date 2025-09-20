"""WHITESPACE optimizer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Choice
from pest.grammar import Rule
from pest.grammar import Sequence

if TYPE_CHECKING:
    from pest.grammar import Expression


# def inline_comment_whitespace(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
#     """"""
#     ws = rules.get("WHITESPACE")
#     if not ws:
#         return expr

#     if isinstance(expr, Sequence):
