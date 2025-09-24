"""JSONPath exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pest import Pair


class JSONPathError(Exception):
    """Base class for all JSONPath exceptions."""

    def __init__(self, *args: object, token: Pair | None = None) -> None:
        super().__init__(*args)
        self.token = token


class JSONPathSyntaxError(JSONPathError):
    """An exception raised due to invalid JSONPath syntax."""


class JSONPathTypeError(JSONPathError):
    """An exception raised due to JSONPath type system errors."""
