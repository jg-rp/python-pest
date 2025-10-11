"""A pest grammar expression group."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar import Expression

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.pairs import Pair
    from pest.state import ParserState


class Group(Expression):
    """A pest grammar expression group.

    This corresponds to `(EXPRESSION)` in pest.

    NOTE: Strictly we don't need to model a group explicitly, but it does make
    it easy to produce accurate string representations of a grammar's parse
    tree before optimization, especially for tagged groups.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}({self.expression})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Group) and self.expression == other.expression

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:
        """Try to parse all parts in sequence starting at `pos`.

        Returns:
            - (Node, new_pos) if all parts match in order.
            - None if any part fails.
        """
        if self.tag:
            with state.tag(self.tag):
                return self.expression.parse(state, pairs)

        return self.expression.parse(state, pairs)

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python source code that implements this grammar expression."""
        gen.writeln("# <Group>")

        if self.tag:
            gen.writeln(f"with state.tag({self.tag!r}):")
            with gen.block():
                self.expression.generate(gen, matched_var, pairs_var)
        else:
            self.expression.generate(gen, matched_var, pairs_var)

        gen.writeln("# </Group>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)
