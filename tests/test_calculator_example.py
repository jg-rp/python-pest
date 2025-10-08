import os
import sys

import pytest

from pest import Parser

# Always regenerate the calculator parser before running tests.
with open("examples/calculator/calculator.pest", encoding="utf-8") as fd:
    parser = Parser.from_grammar(fd.read())

with open("examples/calculator/parser.py", "w", encoding="utf-8") as fd:
    fd.write(parser.generate())

sys.path.append(os.getcwd())

from examples.calculator._ast import Expression
from examples.calculator._ast import InfixExpr
from examples.calculator._ast import IntExpr
from examples.calculator._ast import PostfixExpr
from examples.calculator._ast import PrefixExpr
from examples.calculator._ast import VarExpr
from examples.calculator.calculator import parse_program
from examples.calculator.parser import Rule
from examples.calculator.parser import parse
from pest import PestParsingError


def parse_expression(source: str) -> Expression:
    """Helper to parse a full expression string into an AST node."""
    pairs = parse(Rule.PROGRAM, source)
    return parse_program(pairs)


def eval_expr(source: str, env: dict[str, int] | None = None) -> int:
    """Parse and immediately evaluate an expression."""
    expr = parse_expression(source)
    return expr.evaluate(env or {})


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("0", 0),
        ("42", 42),
        ("123", 123),
    ],
)
def test_simple_literals(source: str, expected: int):
    expr = parse_expression(source)
    assert isinstance(expr, IntExpr)
    assert expr.evaluate({}) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1 + 2", 3),
        ("7 - 3", 4),
        ("2 * 3 + 4", 10),
        ("2 + 3 * 4", 14),
        ("10 / 2", 5),
        ("(1 + 2) * 3", 9),
    ],
)
def test_basic_arithmetic(source: str, expected: int):
    assert eval_expr(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("-5", -5),
        ("--5", 5),
        ("5!", 120),
        ("3!!", 720),
        ("-(3!)", -6),
    ],
)
def test_prefix_and_postfix(source: str, expected: int):
    assert eval_expr(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("2 ^ 3", 8),
        ("2 ^ 3 ^ 2", 512),  # right-associative
        ("2 * 3 ^ 2", 18),
    ],
)
def test_exponentiation_and_precedence(source: str, expected: int):
    assert eval_expr(source) == expected


@pytest.mark.parametrize(
    ("source", "env", "expected"),
    [
        ("x + y", {"x": 2, "y": 3}, 5),
        ("x * y + 1", {"x": 2, "y": 3}, 7),
        ("(x + 1) * y", {"x": 2, "y": 3}, 9),
        ("n!", {"n": 4}, 24),
        ("n!!", {"n": 3}, 720),
    ],
)
def test_variables_and_factorials(source: str, env: dict[str, int], expected: int):
    assert eval_expr(source, env) == expected


@pytest.mark.parametrize(
    ("source", "expected_type"),
    [
        ("1 + 2 * 3", InfixExpr),
        ("-x", PrefixExpr),
        ("5!", PostfixExpr),
        ("x", VarExpr),
    ],
)
def test_ast_shapes(source: str, expected_type: type[Expression]):
    expr = parse_expression(source)
    assert isinstance(expr, expected_type)


@pytest.mark.parametrize(
    ("source", "exc_type"),
    [
        ("1 +", PestParsingError),
        ("1 + * 2", PestParsingError),
        ("x + 1", KeyError),
    ],
)
def test_error_conditions(source: str, exc_type: type[Exception]):
    with pytest.raises(exc_type):
        eval_expr(source)
