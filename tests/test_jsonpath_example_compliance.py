"""Compare our JSONPath implementation with the JSONPath Compliance Test Suite."""

from __future__ import annotations

import json
import operator
import os
import sys
import types
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

import pytest

sys.path.append(os.getcwd())

from examples.jsonpath.exceptions import JSONPathError
from examples.jsonpath.jsonpath import JSONPathParser
from examples.jsonpath.jsonpath import grammar
from pest import Parser

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

    from examples.jsonpath.types import JSONValue
    from pest import Pairs


@dataclass
class Case:
    name: str
    selector: str
    document: JSONValue = None
    result: Any = None
    result_paths: list[Any] | None = None
    results: list[Any] | None = None
    results_paths: list[Any] | None = None
    invalid_selector: bool | None = None
    tags: list[str] = field(default_factory=list[str])


# We're skipping these because we don't want to depend on the `regex` package
# for the sake of an example. The regex package supports Unicode properties,
# `re` from the standard Python library does not.
SKIP = {
    "functions, match, filter, match function, unicode char class, uppercase",
    "functions, match, filter, match function, unicode char class negated, uppercase",
    "functions, match, dot matcher on \\u2028",
    "functions, match, dot matcher on \\u2029",
    "functions, search, filter, search function, unicode char class, uppercase",
    "functions, search, filter, search function, unicode char class negated, uppercase",
    "functions, search, dot matcher on \\u2028",
    "functions, search, dot matcher on \\u2029",
}


def cases() -> list[Case]:
    with open("../jsonpath-compliance-test-suite/cts.json", encoding="utf8") as fd:
        data = json.load(fd)
    return [Case(**case) for case in data["tests"]]


def valid_cases() -> list[Case]:
    return [case for case in cases() if not case.invalid_selector]


def invalid_cases() -> list[Case]:
    return [case for case in cases() if case.invalid_selector]


class GeneratedParser:
    def __init__(self, code: str, *, module_name: str = "generated_parser"):
        # Create an in-memory module for the generated code
        module = types.ModuleType(module_name)
        exec(compile(code, filename=f"{module_name}.py", mode="exec"), module.__dict__)  # noqa: S102
        # Keep a reference to the generated entry point
        self._parse = module.parse

    def parse(self, start_rule: str, input_: str, *, start_pos: int = 0) -> Pairs:
        return self._parse(start_rule, input_, start_pos=start_pos)


class UnoptimizedJSONPathParser(JSONPathParser):
    PARSER = Parser.from_grammar(grammar, optimizer=None)


class GeneratedJSONPathParser(JSONPathParser):
    PARSER = GeneratedParser(Parser.from_grammar(grammar).generate())


class UnoptimizedGeneratedJSONPathParser(JSONPathParser):
    PARSER = GeneratedParser(Parser.from_grammar(grammar, optimizer=None).generate())


@pytest.fixture(
    scope="module",
    params=["not optimized", "optimized", "generated", "optimized generated"],
)
def jsonpath(request: SubRequest) -> JSONPathParser:
    assert isinstance(request.param, str)
    if request.param == "not optimized":
        return UnoptimizedJSONPathParser()
    if request.param == "optimized":
        return JSONPathParser()
    if request.param == "generated":
        return UnoptimizedGeneratedJSONPathParser()
    assert request.param == "optimized generated"
    return GeneratedJSONPathParser()


@pytest.mark.parametrize("case", valid_cases(), ids=operator.attrgetter("name"))
def test_compliance(jsonpath: JSONPathParser, case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    assert case.document is not None
    query = jsonpath.parse(case.selector)
    nodes = query.find(case.document)

    if case.results is not None:
        assert isinstance(case.results_paths, list)
        assert nodes.values() in case.results
        assert nodes.paths() in case.results_paths
    else:
        assert nodes.values() == case.result
        assert nodes.paths() == case.result_paths


@pytest.mark.parametrize("case", invalid_cases(), ids=operator.attrgetter("name"))
def test_invalid_selectors(jsonpath: JSONPathParser, case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    with pytest.raises(JSONPathError):
        jsonpath.parse(case.selector)
