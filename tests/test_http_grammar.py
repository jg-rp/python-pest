import pytest
from _pytest.fixtures import SubRequest

from pest import DEFAULT_OPTIMIZER
from pest import Parser


@pytest.fixture(scope="module", params=["not optimized", "optimized"])
def parser(request: SubRequest) -> Parser:
    optimizer = DEFAULT_OPTIMIZER if request.param == "optimized" else None
    with open("tests/grammars/http.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read(), optimizer=optimizer)


def test_method_rule(parser: Parser) -> None:
    pairs = parser.parse("method", "GET")
    assert pairs.as_list() == [
        {"rule": "method", "span": {"str": "GET", "start": 0, "end": 3}, "inner": []}
    ]


def test_uri_rule(parser: Parser) -> None:
    pairs = parser.parse("uri", "/")
    assert pairs.as_list() == [
        {"rule": "uri", "span": {"str": "/", "start": 0, "end": 1}, "inner": []}
    ]


def test_version_rule(parser: Parser) -> None:
    pairs = parser.parse("version", "1.1")
    assert pairs.as_list() == [
        {"rule": "version", "span": {"str": "1.1", "start": 0, "end": 3}, "inner": []}
    ]


def test_header(parser: Parser) -> None:
    pairs = parser.parse("header", "Connection: keep-alive\n")
    assert pairs.as_list() == [
        {
            "rule": "header",
            "span": {"str": "Connection: keep-alive\n", "start": 0, "end": 23},
            "inner": [
                {
                    "rule": "header_name",
                    "span": {"str": "Connection", "start": 0, "end": 10},
                    "inner": [],
                },
                {
                    "rule": "header_value",
                    "span": {"str": "keep-alive", "start": 12, "end": 22},
                    "inner": [],
                },
            ],
        }
    ]


def test_example(parser: Parser) -> None:
    with open("tests/examples/example.http", encoding="ascii") as fd:
        example = fd.read()

    parser.parse("http", example)
