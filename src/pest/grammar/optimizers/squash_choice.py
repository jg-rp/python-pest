"""Transform choice of literals into a single regex expression."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Choice
from pest.grammar import Rule
from pest.grammar import Sequence
from pest.grammar import CIString
from pest.grammar import String
from pest.grammar import RegexExpression


if TYPE_CHECKING:
    from pest.grammar import Expression


def squash_choice(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    """Transform choice of literals into a single regex expression."""
    # match expr:
    #     case Choice(expressions=exprs) if all(isinstance(expr, String, CIString)):
    #         return RegexExpression("".join)
    # TODO:
    raise NotImplementedError
