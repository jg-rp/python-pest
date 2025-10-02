import pytest
from _pytest.fixtures import SubRequest

from pest import DEFAULT_OPTIMIZER
from pest import Parser


@pytest.fixture(scope="module", params=["not optimized", "optimized"])
def parser(grammar: str, request: SubRequest) -> Parser:
    optimizer = DEFAULT_OPTIMIZER if request.param == "optimized" else None
    return Parser.from_grammar(grammar, optimizer=optimizer)
