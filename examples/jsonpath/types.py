from typing import Any
from typing import TypeAlias

JSONValue: TypeAlias = list[Any] | dict[str, Any] | str | int | float | None | bool

"""JSON-like data, as you would get from `json.load()`."""
