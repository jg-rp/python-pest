"""Example calculator precedence climbing parser.

If running this from the root of the Python pest repo, use
`python -m examples.calculator`
"""

from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Iterator
from enum import IntEnum

from pest import Pair

from .parser import Rule
from .parser import parse


class Precedence(IntEnum):
    """Operator precedence."""

    LOWEST = 1
    ADD_SUB = 3
    MUL_DIV = 4
    POW = 5
    PRE = 6
    FAC = 7


PRECEDENCES = {
    "add": Precedence.ADD_SUB,
    "sub": Precedence.ADD_SUB,
    "mul": Precedence.MUL_DIV,
    "div": Precedence.MUL_DIV,
    "pow": Precedence.POW,
    "fac": Precedence.FAC,
}

PREFIX_OPERATORS = frozenset(["neg"])
POSTFIX_OPERATORS = frozenset(["fac"])
RIGHT_ASSOC = frozenset(["pow"])


class CalcSyntaxError(Exception):
    """Exception raised when there is a syntax error."""


class Expression:
    """Base class for all expressions or sub expressions."""

    @abstractmethod
    def evaluate(self) -> int:
        """Evaluate this expression."""


class IntExpr(Expression):
    def __init__(self, value: int) -> None:
        super().__init__()
        self.value = value

    def evaluate(self) -> int:
        return self.value


class PrefixExpr(Expression):
    def __init__(self, op: Callable[[int], int], expr: Expression) -> None:
        super().__init__()
        self.op = op
        self.expr = expr

    def evaluate(self) -> int:
        return self.op(self.expr.evaluate())


class InfixExpr(Expression):
    def __init__(
        self, op: Callable[[int, int], int], left: Expression, right: Expression
    ) -> None:
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def evaluate(self) -> int:
        return self.op(self.left.evaluate(), self.right.evaluate())


class PostfixExpr(Expression):
    def __init__(self, op: Callable[[int], int], expr: Expression) -> None:
        super().__init__()
        self.op = op
        self.expr = expr

    def evaluate(self) -> int:
        return self.op(self.expr.evaluate())


def parse_expr(pairs: Iterator[Pair]) -> Expression:
    pair = next(pairs, None)

    expr: Expression

    match pair:
        case Pair(Rule.NEG):
            expr = parse_prefix_expression(pair, pairs)
        case Pair(Rule.ADD | Rule.SUB | Rule.MUL | Rule.DIV | Rule.POW):
            expr = parse_infix_expression(pair, pairs)
        case None:
            raise CalcSyntaxError("unexpected end of expression")
        case _:
            expr = parse_primary(pair)  # TODO: assert EOI?

    pair = next(pairs, None)

    if pair.rule.name == Rule.FAC:
        expr = parse_postfix_expression(pair, expr)

    return expr


def parse_prefix_expression(pair: Pair, pairs: Iterator[Pair]) -> PrefixExpr:
    right = next(pairs, None)

    if right is None:
        raise CalcSyntaxError("unexpected end of expression")

    if pair.rule.name == Rule.NEG:
        return PrefixExpr(lambda i: -i, parse_expr(pairs))

    raise CalcSyntaxError(f"unknown prefix operator {pair.text!r}")


def parse_infix_expression(pair: Pair, pairs: Iterator[Pair]) -> InfixExpr:
    raise NotImplementedError


def parse_postfix_expression(pair: Pair, pairs: Iterator[Pair]) -> PostfixExpr:
    raise NotImplementedError


def parse_primary(pair: Pair) -> Expression:
    match pair:
        case Pair(Rule.INT):
            return IntExpr(int(pair.text))
        case Pair(Rule.EXPR):
            return parse_expr(iter(pair))
        case _:
            raise CalcSyntaxError(f"unexpected {pair.text!r}")


def main() -> None:
    # TODO: get expression from stdin
    pairs = parse(Rule.PROGRAM, "1 + 2")
    expr = parse_expr(iter(pairs.first()))
    print(expr.evaluate())


if __name__ == "__main__":
    main()
