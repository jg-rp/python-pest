"""Base class and standard function extensions."""

from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Sized

from ._types import ExpressionType
from .filter_expression import NOTHING
from .filter_expression import Nothing

if TYPE_CHECKING:
    from .node import JSONPathNodeList


class FilterFunction(ABC):
    """Base class for typed function extensions."""

    @property
    @abstractmethod
    def arg_types(self) -> list[ExpressionType]:
        """Argument types expected by the filter function."""

    @property
    @abstractmethod
    def return_type(self) -> ExpressionType:
        """The type of the value returned by the filter function."""

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Called the filter function."""


class Count(FilterFunction):
    """The built-in `count` function."""

    arg_types = [ExpressionType.NODES]
    return_type = ExpressionType.VALUE

    def __call__(self, node_list: JSONPathNodeList) -> int:
        """Return the number of nodes in the node list."""
        return len(node_list)


class Length(FilterFunction):
    """The standard `length` function."""

    arg_types = [ExpressionType.VALUE]
    return_type = ExpressionType.VALUE

    def __call__(self, obj: Sized) -> int | Nothing:
        """Return an object's length.

        If the object does not have a length, the special _Nothing_ value is
        returned.
        """
        try:
            return len(obj)
        except TypeError:
            return NOTHING


class Match(FilterFunction):
    """The standard `match` function."""

    arg_types = [ExpressionType.VALUE, ExpressionType.VALUE]
    return_type = ExpressionType.LOGICAL

    def __call__(self, string: str, pattern: object) -> bool:
        """Return `True` if _string_ matches _pattern_, or `False` otherwise."""
        if not isinstance(pattern, str):
            return False

        try:
            # re.fullmatch caches compiled patterns internally
            return bool(re.fullmatch(pattern, string))
        except (TypeError, re.error):
            return False


class Search(FilterFunction):
    """The standard `search` function."""

    arg_types = [ExpressionType.VALUE, ExpressionType.VALUE]
    return_type = ExpressionType.LOGICAL

    def __call__(self, string: str, pattern: object) -> bool:
        """Return `True` if _string_ contains _pattern_, or `False` otherwise."""
        if not isinstance(pattern, str):
            return False

        try:
            # re.search caches compiled patterns internally
            return bool(re.search(pattern, string))
        except (TypeError, re.error):
            return False


class Value(FilterFunction):
    """The standard `value` function."""

    arg_types = [ExpressionType.NODES]
    return_type = ExpressionType.VALUE

    def __call__(self, nodes: JSONPathNodeList) -> object:
        """Return the first node in a node list if it has only one item."""
        if len(nodes) == 1:
            return nodes[0].value
        return NOTHING
