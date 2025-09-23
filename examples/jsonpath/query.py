"""A compiled JSONPath expression ready to be applied to JSON-like data."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterable

from ._ast import IndexSelector
from ._ast import NameSelector
from ._ast import RecursiveDescentSegment
from .node import JSONPathNode
from .node import JSONPathNodeList

if TYPE_CHECKING:
    from ._ast import Segment
    from .types import JSONValue


class JSONPathQuery:
    """A compiled JSONPath expression ready to be applied to JSON-like data."""

    __slots__ = ("env", "segments")

    def __init__(
        self,
        segments: list[Segment],
    ) -> None:
        self.segments = segments

    def __str__(self) -> str:
        return "$" + "".join(str(segment) for segment in self.segments)

    def __hash__(self) -> int:
        return hash(self.segments)

    def finditer(
        self,
        value: JSONValue,
    ) -> Iterable[JSONPathNode]:
        """Generate `JSONPathNode` instances for each match of this query in value.

        Arguments:
            value: JSON-like data to query, as you'd get from `json.load`.

        Returns:
            An iterator yielding `JSONPathNode` objects for each match.

        Raises:
            JSONPathSyntaxError: If the query is invalid.
            JSONPathTypeError: If a filter expression attempts to use types in
                an incompatible way.
        """
        nodes: Iterable[JSONPathNode] = [
            JSONPathNode(
                value=value,
                location=(),
                root=value,
            )
        ]

        for segment in self.segments:
            nodes = segment.resolve(nodes)

        return nodes

    def find(
        self,
        value: JSONValue,
    ) -> JSONPathNodeList:
        """Apply this JSONPath expression to JSON-like _value_ and return a node list.

        Arguments:
            value: JSON-like data to query, as you'd get from `json.load`.

        Returns:
            A list of `JSONPathNode` instance.

        Raises:
            JSONPathSyntaxError: If the query is invalid.
            JSONPathTypeError: If a filter expression attempts to use types in
                an incompatible way.
        """
        return JSONPathNodeList(self.finditer(value))

    apply = find

    def find_one(self, value: JSONValue) -> JSONPathNode | None:
        """Return the first node from applying this query to _value_.

        Arguments:
            value: JSON-like data to query, as you'd get from `json.load`.

        Returns:
            The first available `JSONPathNode` instance, or `None` if there
                are no matches.

        Raises:
            JSONPathSyntaxError: If the query is invalid.
            JSONPathTypeError: If a filter expression attempts to use types in
                an incompatible way.
        """
        try:
            return next(iter(self.finditer(value)))
        except StopIteration:
            return None

    def singular_query(self) -> bool:
        """Return `True` if this JSONPath expression is a singular query."""
        for segment in self.segments:
            if isinstance(segment, RecursiveDescentSegment):
                return False

            if len(segment.selectors) == 1 and isinstance(
                segment.selectors[0], (NameSelector, IndexSelector)
            ):
                continue

            return False

        return True

    def empty(self) -> bool:
        """Return `True` if this query has no segments."""
        return not bool(self.segments)
