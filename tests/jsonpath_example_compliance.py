"""Compare our JSONPath implementation with the JSONPath Compliance Test Suite."""

import json
import operator
import os
import sys
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pytest

sys.path.append(os.getcwd())

from examples.jsonpath.exceptions import JSONPathError
from examples.jsonpath.jsonpath import JSONPathParser
from examples.jsonpath.types import JSONValue


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
    tags: list[str] = field(default_factory=list)


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


@pytest.fixture(scope="module")
def parser() -> JSONPathParser:
    return JSONPathParser()


@pytest.mark.parametrize("case", valid_cases(), ids=operator.attrgetter("name"))
def test_compliance(parser: JSONPathParser, case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    assert case.document is not None
    query = parser.parse(case.selector)
    nodes = query.find(case.document)

    if case.results is not None:
        assert isinstance(case.results_paths, list)
        assert nodes.values() in case.results
        assert nodes.paths() in case.results_paths
    else:
        assert nodes.values() == case.result
        assert nodes.paths() == case.result_paths


@pytest.mark.parametrize("case", invalid_cases(), ids=operator.attrgetter("name"))
def test_invalid_selectors(parser: JSONPathParser, case: Case) -> None:
    if case.name in SKIP:
        pytest.skip()

    with pytest.raises(JSONPathError):
        parser.parse(case.selector)
