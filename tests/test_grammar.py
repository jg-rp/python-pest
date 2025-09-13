import pytest

from pest import Parser


@pytest.fixture(scope="module")
def parser() -> Parser:
    with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read())


def test_string_rule(parser: Parser) -> None:
    pairs = parser.parse("string", "abc")
    assert pairs.as_list() == []
