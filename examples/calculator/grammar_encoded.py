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
from .grammar_encoded_prec_parser import Rule
from .grammar_encoded_prec_parser import parse


def parse_program(pairs: Pairs) -> Expression:
    return parse_expr(pairs.first().inner().first())


def parse_expr(pair: Pair) -> Expression:
    """program → expr"""
    match pair:
        case Pair(Rule.EXPR, [expr]):
            return parse_add_sub(expr)
        case _:
            raise SyntaxError(f"expected program, got {pair.name}")


def parse_add_sub(pair: Pair) -> Expression:
    """add_sub → mul_div ( ( '+' | '-' ) mul_div )*"""
    match pair:
        case Pair(Rule.ADD_SUB, [single]):
            return parse_mul_div(single)
        case Pair(Rule.ADD_SUB, [left, op, right, *rest]):
            left_expr = InfixExpr(
                add if op.name == "add" else sub,
                parse_mul_div(left),
                parse_mul_div(right),
            )
            # fold any remaining ops in sequence
            while rest:
                op, right, *rest = rest
                func = add if op.name == "add" else sub
                left_expr = InfixExpr(func, left_expr, parse_mul_div(right))
            return left_expr
        case _:
            raise SyntaxError(f"unexpected structure in add_sub: {pair}")


def parse_mul_div(pair: Pair) -> Expression:
    """mul_div → pow_expr ( ( '*' | '/' ) pow_expr )*"""
    match pair:
        case Pair(Rule.MUL_DIV, [single]):
            return parse_pow_expr(single)
        case Pair(Rule.MUL_DIV, [left, op, right, *rest]):
            left_expr = InfixExpr(
                mul if op.name == "mul" else floordiv,
                parse_pow_expr(left),
                parse_pow_expr(right),
            )
            while rest:
                op, right, *rest = rest
                func = mul if op.name == "mul" else floordiv
                left_expr = InfixExpr(func, left_expr, parse_pow_expr(right))
            return left_expr
        case _:
            raise SyntaxError(f"unexpected structure in mul_div: {pair}")


def parse_pow_expr(pair: Pair) -> Expression:
    """pow_expr → prefix ( '^' pow_expr )?"""
    match pair:
        case Pair("pow_expr", [prefix]):
            return parse_prefix(prefix)
        case Pair("pow_expr", [left, op, right]):
            return InfixExpr(pow, parse_prefix(left), parse_pow_expr(right))
        case _:
            raise SyntaxError(f"unexpected structure in pow_expr: {pair}")


def parse_prefix(pair: Pair) -> Expression:
    """prefix → ('-')* postfix"""
    match pair:
        case Pair("prefix", [postfix]):
            return parse_postfix(postfix)
        case Pair("prefix", [op, rest]):
            expr = parse_prefix(rest)
            if op.name == "neg":
                return PrefixExpr(neg, expr)
            raise SyntaxError(f"unknown prefix op {op.name}")
        case _:
            raise SyntaxError(f"unexpected structure in prefix: {pair}")


def parse_postfix(pair: Pair) -> Expression:
    """postfix → primary ('!')*"""
    match pair:
        case Pair("postfix", [primary]):
            return parse_primary(primary)
        case Pair("postfix", [inner, op]):
            expr = parse_primary(inner)
            if op.name == "fac":
                return PostfixExpr(factorial, expr)
            raise SyntaxError(f"unknown postfix op {op.name}")
        case _:
            raise SyntaxError(f"unexpected structure in postfix: {pair}")


def parse_primary(pair: Pair) -> Expression:
    """primary → int | ident | '(' expr ')'"""
    match pair:
        case Pair("int", []):
            return IntExpr(int(pair.text))
        case Pair("ident", []):
            return VarExpr(pair.text)
        case Pair("expr", [inner]):
            return parse_add_sub(inner)
        case _:
            raise SyntaxError(f"unexpected structure in primary: {pair}")


def example() -> None:
    pairs = parse(Rule.PROGRAM, "1 + 2 + x")
    prog = parse_program(pairs)
    print(prog.evaluate({"x": 42}))  # noqa: T201


if __name__ == "__main__":
    example()
