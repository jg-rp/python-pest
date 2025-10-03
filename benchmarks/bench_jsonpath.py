from __future__ import annotations

import json
import os
import sys
import timeit
import types
from typing import TYPE_CHECKING
from typing import Any
from typing import NamedTuple

from pest import Parser

sys.path.append(os.getcwd())

from examples.jsonpath.jsonpath import JSONPathParser
from examples.jsonpath.jsonpath import grammar

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

    from pest import Pairs


class GeneratedParser:
    def __init__(self, code: str, *, module_name: str = "generated_parser"):
        # Create an in-memory module for the generated code
        module = types.ModuleType(module_name)
        exec(compile(code, filename=f"{module_name}.py", mode="exec"), module.__dict__)  # noqa: S102
        # Keep a reference to the generated entry point
        self._parse = module.parse

    def parse(self, start_rule: str, input_: str, *, start_pos: int = 0) -> Pairs:  # noqa: D102
        return self._parse(start_rule, input_, start_pos=start_pos)


class UnoptimizedJSONPathParser(JSONPathParser):
    PARSER = Parser.from_grammar(grammar, optimizer=None)


class GeneratedJSONPathParser(JSONPathParser):
    PARSER = GeneratedParser(Parser.from_grammar(grammar).generate())


class UnoptimizedGeneratedJSONPathParser(JSONPathParser):
    PARSER = GeneratedParser(Parser.from_grammar(grammar, optimizer=None).generate())


class CTSCase(NamedTuple):
    query: str
    data: Sequence[Any] | Mapping[str, Any]


def valid_queries() -> Sequence[CTSCase]:
    with open("../jsonpath-compliance-test-suite/cts.json") as fd:
        data = json.load(fd)

    return [
        (CTSCase(t["selector"], t["document"]))
        for t in data["tests"]
        if not t.get("invalid_selector", False)
    ]


QUERIES = valid_queries()
PEST = GeneratedParser(Parser.from_grammar(grammar).generate())

COMPILE_AND_FIND_STMT = """\
for path, data in QUERIES:
    list(PARSER.parse(path).find(data))"""

JUST_PARSE_STMT = """\
for path, _ in QUERIES:
    PEST.parse("jsonpath", path)"""

JUST_COMPILE_STMT = """\
for path, _ in QUERIES:
    PARSER.parse(path)"""

JUST_FIND_SETUP = """\
compiled_queries = [(PARSER.parse(q), d) for q, d in QUERIES]
"""

JUST_FIND_STMT = """\
for path, data in compiled_queries:
    list(path.find(data))"""


def benchmark(number: int = 10, best_of: int = 3) -> None:
    print(f"repeating {len(QUERIES)} queries {number} times, best of {best_of} rounds")

    results = timeit.repeat(
        COMPILE_AND_FIND_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": GeneratedJSONPathParser(),
        },
        number=number,
        repeat=best_of,
    )
    print("compile and find".ljust(38), f"\033[92m{min(results):.3f}\033[0m")

    results = timeit.repeat(
        JUST_PARSE_STMT,
        globals={
            "QUERIES": QUERIES,
            "PEST": PEST,
        },
        number=number,
        repeat=best_of,
    )
    print("just pest parse".ljust(38), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_COMPILE_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": JSONPathParser(),
        },
        number=number,
        repeat=best_of,
    )
    print("just compile (optimized)".ljust(38), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_COMPILE_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": UnoptimizedGeneratedJSONPathParser(),
        },
        number=number,
        repeat=best_of,
    )
    print("just compile (unoptimized)".ljust(38), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_COMPILE_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": GeneratedJSONPathParser(),
        },
        number=number,
        repeat=best_of,
    )
    print("just compile (generated)".ljust(38), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_COMPILE_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": UnoptimizedGeneratedJSONPathParser(),
        },
        number=number,
        repeat=best_of,
    )
    print("just compile (generated unoptimized)".ljust(38), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_FIND_STMT,
        setup=JUST_FIND_SETUP,
        globals={
            "QUERIES": QUERIES,
            "PARSER": JSONPathParser(),
        },
        number=number,
        repeat=best_of,
    )
    print("just find".ljust(38), f"\033[92m{min(results):.3f}\033[0m")


if __name__ == "__main__":
    benchmark()
