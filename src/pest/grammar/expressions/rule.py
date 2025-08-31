"""A logical grammar rule."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Expression
from pest.node import Node
from pest.result import ParseResult

if TYPE_CHECKING:
    from pest.state import ParserState


class Rule(Expression):
    """A named grammar rule."""

    __slots__ = ("name", "modifier", "expression", "doc")

    def __init__(
        self,
        name: str,
        expression: Expression,
        modifier: str | None = None,
        doc: list[str] | None = None,
    ):
        super().__init__(tag=None)
        self.name = name
        self.expression = expression
        self.modifier = modifier
        self.doc = doc

    def __str__(self) -> str:
        doc = "".join(f"///{line}\n" for line in self.doc) if self.doc else ""
        modifier = self.modifier if self.modifier else ""
        return f"{doc}{self.name} = {modifier}{{ {self.expression} }}"

    def parse(self, state: ParserState, start: int) -> ParseResult | None:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.

        Returns:
            If parsing succeeds, a `Node` representing the result of the
            matched expression and any child expressions. Or `None` if the
            expression fails to match at `pos`.
        """
        restore_atomic_depth = state.atomic_depth

        if self.modifier in ("@", "$"):
            state.atomic_depth += 1
        elif self.modifier == "!":
            state.atomic_depth = 0

        try:
            result = self.expression.parse(state, start)
            if result is None:
                return None

            node, end = result.node, result.pos

            # Silent rule succeeds, but no node is returned.
            if self.modifier == "_":
                return ParseResult(node=None, pos=end)

            # Compound-atomic rule discards children
            if self.modifier == "$":
                return ParseResult(
                    node=Node(rule=self, start=start, end=end, children=[]),
                    pos=end,
                )

            return ParseResult(
                node=Node(
                    rule=self,
                    start=start,
                    end=end,
                    children=[node] if node else [],
                ),
                pos=end,
            )
        finally:
            # Restore atomic depth to what it was before this rule
            state.atomic_depth = restore_atomic_depth
