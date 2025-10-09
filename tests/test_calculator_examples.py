import os
import sys
from collections.abc import Callable

import pytest
from _pytest.fixtures import SubRequest

from pest import Parser

# Always regenerate the calculator parser before running tests.
with open("examples/calculator/calculator.pest", encoding="utf-8") as fd:
    _parser = Parser.from_grammar(fd.read())

with open("examples/calculator/parser.py", "w", encoding="utf-8") as fd:
    fd.write(_parser.generate())

with open("examples/calculator/grammar_encoded_prec.pest") as fd:
    _parser = Parser.from_grammar(fd.read())

with open(
    "examples/calculator/grammar_encoded_prec_parser.py", "w", encoding="utf-8"
) as fd:
    fd.write(_parser.generate())

sys.path.append(os.getcwd())

from examples.calculator._ast import Expression
from examples.calculator._ast import InfixExpr
from examples.calculator._ast import IntExpr
from examples.calculator._ast import PostfixExpr
from examples.calculator._ast import PrefixExpr
from examples.calculator._ast import VarExpr
from examples.calculator.grammar_encoded import parse_program as parse_program_implicit
from examples.calculator.grammar_encoded_prec_parser import parse as parse_implicit
from examples.calculator.parser import Rule
from examples.calculator.parser import parse
from examples.calculator.pratt import CalculatorParser
from examples.calculator.prec_climber import parse_program
from pest import PestParsingError


@pytest.fixture(params=["precedence", "pratt", "grammar"], scope="module")
def parser(request: SubRequest) -> Callable[[str], Expression]:
    """Parameterized fixture providing both parser implementations."""
    if request.param == "precedence":

        def precedence_parser(source: str) -> Expression:
            pairs = parse(Rule.PROGRAM, source)
            return parse_program(pairs)

        return precedence_parser

    if request.param == "pratt":
        pratt_parser = CalculatorParser()

        def pratt_parse(source: str) -> Expression:
            return pratt_parser.parse(source)

        return pratt_parse

    if request.param == "grammar":

        def grammar_parse(source: str) -> Expression:
            pairs = parse_implicit(Rule.PROGRAM, source)
            return parse_program_implicit(pairs)

        return grammar_parse

    raise ValueError(f"Unknown parser type {request.param!r}")


@pytest.fixture
def parse_expression(parser: Callable[[str], Expression]):
    """Fixture returning a callable that parses a source string into an AST."""
    return parser


def eval_expr(
    parse_expression: Callable[[str], Expression],
    source: str,
    env: dict[str, int] | None = None,
) -> int:
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
def test_simple_literals(
    parse_expression: Callable[[str], Expression], source: str, expected: int
):
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
def test_basic_arithmetic(
    parse_expression: Callable[[str], Expression], source: str, expected: int
):
    assert eval_expr(parse_expression, source) == expected


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
def test_prefix_and_postfix(
    parse_expression: Callable[[str], Expression], source: str, expected: int
):
    assert eval_expr(parse_expression, source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("2 ^ 3", 8),
        ("2 ^ 3 ^ 2", 512),  # right-associative
        ("2 * 3 ^ 2", 18),
    ],
)
def test_exponentiation_and_precedence(
    parse_expression: Callable[[str], Expression], source: str, expected: int
):
    assert eval_expr(parse_expression, source) == expected


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
def test_variables_and_factorials(
    parse_expression: Callable[[str], Expression],
    source: str,
    env: dict[str, int],
    expected: int,
):
    assert eval_expr(parse_expression, source, env) == expected


@pytest.mark.parametrize(
    ("source", "expected_type"),
    [
        ("1 + 2 * 3", InfixExpr),
        ("-x", PrefixExpr),
        ("5!", PostfixExpr),
        ("x", VarExpr),
    ],
)
def test_ast_shapes(
    parse_expression: Callable[[str], Expression],
    source: str,
    expected_type: type[Expression],
):
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
def test_error_conditions(
    parse_expression: Callable[[str], Expression],
    source: str,
    exc_type: type[Exception],
):
    with pytest.raises(exc_type):
        eval_expr(parse_expression, source)
