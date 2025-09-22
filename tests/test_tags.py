import pytest
from _pytest.fixtures import SubRequest

from pest import DEFAULT_OPTIMIZER
from pest import Parser

GRAMMAR = """\
expr = {
  SOI ~
  #prefix=(STAR)? ~ #suffix=DOT?
  ~ EOI
}

STAR={"*"}
DOT={"."}"""


@pytest.fixture(scope="module", params=["not optimized", "optimized"])
def parser(request: SubRequest) -> Parser:
    optimizer = DEFAULT_OPTIMIZER if request.param == "optimized" else None
    return Parser.from_grammar(GRAMMAR, optimizer=optimizer)


def test_opt_tag_star(parser: Parser) -> None:
    pairs = parser.parse("expr", "*")
    assert pairs.find_first_tagged("prefix") is not None
    assert pairs.find_first_tagged("suffix") is None


def test_opt_tag_empty(parser: Parser) -> None:
    pairs = parser.parse("expr", "")
    assert pairs.find_first_tagged("prefix") is None
    assert pairs.find_first_tagged("suffix") is None


def test_opt_tag_dot(parser: Parser) -> None:
    pairs = parser.parse("expr", ".")
    assert pairs.find_first_tagged("prefix") is None
    assert pairs.find_first_tagged("suffix") is not None
