from enum import Enum
from typing import Any
from typing import TypeAlias

JSONValue: TypeAlias = list[Any] | dict[str, Any] | str | int | float | None | bool
"""JSON-like data, as you would get from `json.load()`."""


class ExpressionType(Enum):
    """The type of a filter function argument or return value."""

    VALUE = 1
    LOGICAL = 2
    NODES = 3
