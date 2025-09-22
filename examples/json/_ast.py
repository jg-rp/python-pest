"""Example AST for JSON formatted data."""

from __future__ import annotations

import decimal
from abc import ABC
from abc import abstractmethod


class JSONValue(ABC):
    """Base class for JSON AST nodes."""

    @abstractmethod
    def dumps(self) -> str:
        """Return a string representation of this node."""


class JSONObject(JSONValue):
    """A JSON object node."""

    def __init__(self, items: list[tuple[str, JSONValue]]):
        super().__init__()
        self.items = items

    def dumps(self) -> str:
        """Return a string representation of this node."""
        contents = ",".join(f'"{name}":{value.dumps()}' for name, value in self.items)
        return f"{{{contents}}}"


class JSONArray(JSONValue):
    """A JSON array node."""

    def __init__(self, items: list[JSONValue]):
        super().__init__()
        self.items = items

    def dumps(self) -> str:
        """Return a string representation of this node."""
        contents = ",".join(value.dumps() for value in self.items)
        return f"[{contents}]"


class JSONString(JSONValue):
    """A JSON string node."""

    def __init__(self, s: str):
        super().__init__()
        self.s = s

    def dumps(self) -> str:
        """Return a string representation of this node."""
        return f'"{self.s}"'


class JSONNumber(JSONValue):
    """A JSON number node."""

    def __init__(self, n: int | float):
        super().__init__()
        self.n = n

    def dumps(self) -> str:
        """Return a string representation of this node."""
        return f"{self.n:f}"


class JSONBool(JSONValue):
    """A JSON Boolean node."""

    def __init__(self, b: bool):  # noqa: FBT001
        super().__init__()
        self.b = b

    def dumps(self) -> str:
        """Return a string representation of this node."""
        return str(self.b).lower()


class JSONNull(JSONValue):
    """A JSON Null node."""

    def dumps(self) -> str:
        """Return a string representation of this node."""
        return "null"
