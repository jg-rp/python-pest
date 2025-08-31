"""The result of calling `Expression.parse()`."""

from typing import NamedTuple

from .node import Node


class ParseResult(NamedTuple):
    """The result of calling `Expression.parse()`."""

    node: Node | None  # None if silent
    pos: int
