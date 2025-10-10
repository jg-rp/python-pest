"""JSONPath AST built from segments and selectors."""

from __future__ import annotations

import json
from abc import ABC
from abc import abstractmethod
from contextlib import suppress
from typing import TYPE_CHECKING

from .exceptions import JSONPathTypeError
from .filter_expression import FilterContext

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Iterator
    from collections.abc import Sequence

    from pest import Pair

    from .filter_expression import FilterExpression
    from .node import JSONPathNode


class Selector(ABC):
    """Base class for all JSONPath selectors."""

    def __init__(self, token: Pair):
        self.token = token

    @abstractmethod
    def resolve(self, node: JSONPathNode) -> Iterator[JSONPathNode]:
        """Apply this selector to `node`."""


class Segment(ABC):
    def __init__(self, token: Pair, selectors: list[Selector]):
        self.token = token
        self.selectors = selectors

    @abstractmethod
    def resolve(self, nodes: Iterable[JSONPathNode]) -> Iterator[JSONPathNode]:
        """Apply this segment to each `JSONPathNode` in _nodes_."""


class NameSelector(Selector):
    """The name selector, shorthand or quoted."""

    def __init__(self, token: Pair, name: str):
        super().__init__(token)
        self.name = name

    def __str__(self) -> str:
        return canonical_string(self.name)

    def resolve(self, node: JSONPathNode) -> Iterator[JSONPathNode]:
        """Apply this selector to `node`."""
        if isinstance(node.value, dict):
            with suppress(KeyError):
                yield node.new_child(node.value[self.name], self.name)


class IndexSelector(Selector):
    """The array index selector."""

    def __init__(self, token: Pair, index: int):
        super().__init__(token)
        self.index = index

    def __str__(self) -> str:
        return str(self.index)

    def _normalized_index(self, obj: Sequence[object]) -> int:
        if self.index < 0 and len(obj) >= abs(self.index):
            return len(obj) + self.index
        return self.index

    def resolve(self, node: JSONPathNode) -> Iterator[JSONPathNode]:
        """Apply this selector to `node`."""
        if isinstance(node.value, list):
            norm_index = self._normalized_index(node.value)
            with suppress(IndexError):
                yield node.new_child(node.value[self.index], norm_index)


class SliceSelector(Selector):
    """The array slice selector."""

    def __init__(
        self,
        token: Pair,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ):
        super().__init__(token)
        self.slice = slice(start, stop, step)

    def __str__(self) -> str:
        stop = self.slice.stop if self.slice.stop is not None else ""
        start = self.slice.start if self.slice.start is not None else ""
        step = self.slice.step if self.slice.step is not None else "1"
        return f"{start}:{stop}:{step}"

    def resolve(self, node: JSONPathNode) -> Iterator[JSONPathNode]:
        """Apply this selector to `node`."""
        if isinstance(node.value, list) and self.slice.step != 0:
            for idx, element in zip(  # noqa: B905
                range(*self.slice.indices(len(node.value))), node.value[self.slice]
            ):
                yield node.new_child(element, idx)


class WildcardSelector(Selector):
    """The wildcard selector."""

    def __str__(self) -> str:
        return "*"

    def resolve(self, node: JSONPathNode) -> Iterator[JSONPathNode]:
        """Apply this selector to `node`."""
        if isinstance(node.value, dict):
            for name, val in node.value.items():
                yield node.new_child(val, name)

        elif isinstance(node.value, list):
            for i, element in enumerate(node.value):
                yield node.new_child(element, i)


class FilterSelector(Selector):
    """Filter array/list items or dict/object values with a filter expression."""

    def __init__(self, token: Pair, expression: FilterExpression):
        super().__init__(token)
        self.expression = expression

    def __str__(self) -> str:
        return f"?{self.expression}"

    def resolve(self, node: JSONPathNode) -> Iterator[JSONPathNode]:
        """Apply this selector to `node`."""
        if isinstance(node.value, dict):
            for name, val in node.value.items():
                context = FilterContext(
                    current=val,
                    root=node.root,
                )
                try:
                    if self.expression.evaluate(context):
                        yield node.new_child(val, name)
                except JSONPathTypeError as err:
                    if not err.token:
                        err.token = self.token
                    raise

        elif isinstance(node.value, list):
            for i, element in enumerate(node.value):
                context = FilterContext(
                    current=element,
                    root=node.root,
                )
                try:
                    if self.expression.evaluate(context):
                        yield node.new_child(element, i)
                except JSONPathTypeError as err:
                    if not err.token:
                        err.token = self.token
                    raise


class ChildSegment(Segment):
    """The JSONPath child selection segment."""

    def resolve(self, nodes: Iterable[JSONPathNode]) -> Iterator[JSONPathNode]:
        """Apply this segment to each `JSONPathNode` in _nodes_."""
        for node in nodes:
            for selector in self.selectors:
                yield from selector.resolve(node)

    def __str__(self) -> str:
        return f"[{', '.join(str(itm) for itm in self.selectors)}]"


class RecursiveDescentSegment(Segment):
    """The JSONPath recursive descent segment."""

    def resolve(self, nodes: Iterable[JSONPathNode]) -> Iterator[JSONPathNode]:
        """Select descendants of each node in _nodes_."""
        for node in nodes:
            for _node in self._visit(node):
                for selector in self.selectors:
                    yield from selector.resolve(_node)

    def _visit(self, node: JSONPathNode, depth: int = 1) -> Iterable[JSONPathNode]:
        """Depth-first, pre-order node traversal."""
        yield node

        if isinstance(node.value, dict):
            for name, val in node.value.items():
                if isinstance(val, (dict, list)):
                    _node = node.new_child(val, name)
                    yield from self._visit(_node, depth + 1)
        elif isinstance(node.value, list):
            for i, element in enumerate(node.value):
                if isinstance(element, (dict, list)):
                    _node = node.new_child(element, i)
                    yield from self._visit(_node, depth + 1)


def canonical_string(value: str) -> str:
    """Return _value_ as a canonically formatted string literal."""
    single_quoted = (
        json.dumps(value, ensure_ascii=False)[1:-1]
        .replace('\\"', '"')
        .replace("'", "\\'")
    )
    return f"'{single_quoted}'"
