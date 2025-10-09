import json
from math import factorial
from operator import add
from operator import floordiv
from operator import mul
from operator import neg
from operator import sub

from pest import Pair
from pest import Pairs

from ._ast import Expression
from ._ast import InfixExpr
from ._ast import IntExpr
from ._ast import PostfixExpr
from ._ast import PrefixExpr
from ._ast import VarExpr
from .implicit_prec_parser import Rule
from .implicit_prec_parser import parse


def parse_program(program: Pairs) -> Expression:
    assert program.first().name == Rule.PROGRAM
    return parse_expr(program.first().inner().first())


def parse_expr(pair: Pair) -> Expression:
    """program → expr"""
    assert pair.name == Rule.EXPR, f"!!: {pair.name}"
    return parse_add_sub(pair.inner()[0])


def parse_add_sub(pair: Pair) -> Expression:
    """add_sub → mul_div ( ( '+' | '-' ) mul_div )*"""
    inner = pair.inner()
    left = parse_mul_div(inner[0])
    for i in range(1, len(inner), 2):
        op, right = inner[i], inner[i + 1]
        func = add if op.name == Rule.ADD else sub
        left = InfixExpr(func, left, parse_mul_div(right))
    return left


def parse_mul_div(pair: Pair) -> Expression:
    """mul_div → pow_expr ( ( '*' | '/' ) pow_expr )*"""
    inner = pair.inner()
    left = parse_pow_expr(inner[0])
    for i in range(1, len(inner), 2):
        op, right = inner[i], inner[i + 1]
        func = mul if op.name == Rule.MUL else floordiv
        left = InfixExpr(func, left, parse_pow_expr(right))
    return left


def parse_pow_expr(pair: Pair) -> Expression:
    """pow_expr → prefix ( '^' pow_expr )?  (right-associative)"""
    inner = pair.inner()
    left = parse_prefix(inner[0])
    if len(inner) > 1:
        right = inner[2]
        right_expr = parse_pow_expr(right)
        left = InfixExpr(pow, left, right_expr)
    return left


def parse_prefix(pair: Pair) -> Expression:
    """prefix → ('-')* postfix"""
    inner = pair.inner()
    ops = [p for p in inner if p.name == Rule.NEG]
    target = next(p for p in inner if p.name == Rule.POSTFIX)
    expr = parse_postfix(target)
    for _ in reversed(ops):
        expr = PrefixExpr(neg, expr)
    return expr


def parse_postfix(pair: Pair) -> Expression:
    """postfix → primary ('!')*"""
    inner = pair.inner()
    expr = parse_primary(inner[0])
    for op in inner[1:]:
        if op.name == Rule.FAC:
            expr = PostfixExpr(factorial, expr)
    return expr


def parse_primary(pair: Pair) -> Expression:
    """primary → int | ident | '(' expr ')'"""
    match pair:
        case Pair(Rule.INT):
            return IntExpr(int(pair.text))
        case Pair(Rule.IDENT):
            return VarExpr(pair.text)
        case Pair(Rule.EXPR):
            return parse_add_sub(pair.inner()[0])
        case _:
            raise SyntaxError(f"unexpected {pair.text!r}")


def example() -> None:
    pairs = parse(Rule.PROGRAM, "0")
    prog = parse_program(pairs)
    print(prog.evaluate({"x": 42}))  # noqa: T201


if __name__ == "__main__":
    example()
