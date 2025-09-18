"""WHITESPACE optimizer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Mapping

from pest.grammar import Choice
from pest.grammar import Rule
from pest.grammar import Sequence

if TYPE_CHECKING:
    from pest.grammar import Expression


def whitespace(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:
    """"""
    # TODO:
    raise NotImplementedError
