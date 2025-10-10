"""Generic Pratt parser base class operating on a pest `Stream` of `Pair`s."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from pest import Pair
    from pest import Stream

ExprT = TypeVar("ExprT")


class PrattParser(ABC, Generic[ExprT]):
    """Generic Pratt parser base class operating on a pest `Stream` of `Pair`s.

    Subclasses define how to construct AST nodes by overriding the four
    abstract parse_* methods and providing operator-precedence tables.
    """

    PREFIX_OPS: ClassVar[dict[str, int]] = {}
    """Mapping of prefix operator rule names to precedence levels."""

    POSTFIX_OPS: ClassVar[dict[str, int]] = {}
    """Mapping of postfix operator rule names to precedence levels."""

    INFIX_OPS: ClassVar[dict[str, tuple[int, bool]]] = {}
    """Mapping of infix operator rule names to (precedence, right_associative)."""

    LEFT_ASSOC = False
    """An alias for `False`.
    
    Use it as the second item in `INFIX_OPS` values, right_associative, for
    improved readability.
    """

    RIGHT_ASSOC = True
    """An alias for `True`.
    
    Use it as the second item in `INFIX_OPS` values, right_associative, for
    improved readability.
    """

    @abstractmethod
    def parse_primary(self, pair: Pair) -> ExprT:
        """Parse a primary expression: literal, variable, or parenthesized."""

    @abstractmethod
    def parse_prefix(self, op: Pair, rhs: ExprT) -> ExprT:
        """Build a node for a prefix operator expression."""

    @abstractmethod
    def parse_postfix(self, lhs: ExprT, op: Pair) -> ExprT:
        """Build a node for a postfix operator expression."""

    @abstractmethod
    def parse_infix(self, lhs: ExprT, op: Pair, rhs: ExprT) -> ExprT:
        """Build a node for an infix operator expression."""

    def parse_expr(self, stream: Stream, min_prec: int = 0) -> ExprT:
        """Parse an expression from a pest `Stream` using Pratt precedence rules."""
        token: Pair | None = stream.next()
        if token is None:
            raise SyntaxError("Unexpected end of expression")

        # Handle prefix operators or primary expression
        if token.name in self.PREFIX_OPS:
            prec = self.PREFIX_OPS[token.name]
            rhs = self.parse_expr(stream, prec)
            left: ExprT = self.parse_prefix(token, rhs)
        else:
            left = self.parse_primary(token)

        # Handle infix and postfix operators
        while True:
            next_token: Pair | None = stream.peek()
            if next_token is None:
                break

            # Postfix operator
            if next_token.name in self.POSTFIX_OPS:
                stream.next()
                left = self.parse_postfix(left, next_token)
                continue

            # Infix operator
            if next_token.name in self.INFIX_OPS:
                prec, right_assoc = self.INFIX_OPS[next_token.name]
                if prec < min_prec:
                    break
                stream.next()
                rhs = self.parse_expr(stream, prec + (0 if right_assoc else 1))
                left = self.parse_infix(left, next_token, rhs)
                continue

            break

        return left
