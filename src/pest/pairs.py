"""A `Token` and `Pairs` interface to our internal `Node` data structure."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator

if TYPE_CHECKING:
    from .grammar.expressions.rule import Rule
    from .node import Node


class Token:
    """User-facing token stream element (start or end of a rule).

    Arguments:
        rule: name of the matched rule.
        pos: start position in Unicode code points.
    """

    __slots__ = ("rule", "pos")

    def __init__(self, rule: Rule, pos: int) -> None:
        self.rule = rule
        self.pos = pos


class Start(Token):
    """A token indicating the start of a rule."""

    def __repr__(self) -> str:
        return f"Start(rule={self.rule.name!r}, pos={self.pos})"


class End(Token):
    """A token indicating the end of a rule."""

    def __repr__(self) -> str:
        return f"End(rule={self.rule.name!r}, pos={self.pos})"


class Pair:
    """A single parsed element, corresponding to one rule match."""

    __slots__ = ("rule", "span", "_node")

    def __init__(self, node: Node):
        self._node = node
        self.rule = node.rule
        self.span = node.span()

    def as_str(self, input_str: str) -> str:
        """Return the substring of the original input matched by this pair."""
        start, end = self.span
        return input_str[start:end]

    def into_inner(self) -> "Pairs":
        """Return the child pairs of this pair."""
        return Pairs(self._node.children)


class Pairs:
    """An iterable over instances of `Pair`."""

    __slots__ = ("_nodes",)

    def __init__(self, nodes: list[Node]):
        self._nodes = nodes

    def __iter__(self) -> Iterator[Pair]:
        for node in self._nodes:
            yield Pair(node)

    def tokens(self) -> Iterator[Token]:
        """Emit tokens in start/end order for each node (depth-first)."""
        for node in self._nodes:
            yield from self._tokens_from_node(node)

    def _tokens_from_node(self, node: Node) -> Iterator[Token]:
        yield Start(rule=node.rule, pos=node.start)

        for child in node.children:
            yield from self._tokens_from_node(child)

        yield End(rule=node.rule, pos=node.end)
