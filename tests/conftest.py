from __future__ import annotations

import types
from typing import TYPE_CHECKING
from typing import Protocol

import pytest

from pest import DEFAULT_OPTIMIZER
from pest import Parser

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

    from pest import Pairs


class ParserLike(Protocol):
    def parse(self, start_rule: str, input_: str, *, start_pos: int = 0) -> Pairs: ...


class GeneratedParser:
    def __init__(self, code: str, *, module_name: str = "generated_parser"):
        # Create an in-memory module for the generated code
        module = types.ModuleType(module_name)
        exec(compile(code, filename=f"{module_name}.py", mode="exec"), module.__dict__)  # noqa: S102
        # Keep a reference to the generated entry point
        self._parse = module.parse

    def parse(self, start_rule: str, input_: str, *, start_pos: int = 0) -> Pairs:
        return self._parse(start_rule, input_, start_pos=start_pos)


@pytest.fixture(
    scope="module",
    params=["not optimized", "optimized", "generated", "optimized generated"],
)
def parser(grammar: str, request: SubRequest) -> ParserLike:
    assert isinstance(request.param, str)
    optimizer = DEFAULT_OPTIMIZER if request.param.startswith("optimized") else None
    parser = Parser.from_grammar(grammar, optimizer=optimizer)

    if "generated" in request.param:
        return GeneratedParser(parser.generate())
    return parser
