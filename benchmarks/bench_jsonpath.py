import json
import os
import sys
import timeit
from typing import Any
from typing import Mapping
from typing import NamedTuple
from typing import Sequence
from typing import Union

sys.path.append(os.getcwd())

from examples.jsonpath import compile  # noqa: A004
from examples.jsonpath import find
from examples.jsonpath.jsonpath import PARSER
from examples.jsonpath.jsonpath import JSONPathParser

JP_PARSER = JSONPathParser()


class CTSCase(NamedTuple):
    query: str
    data: Union[Sequence[Any], Mapping[str, Any]]


def valid_queries() -> Sequence[CTSCase]:
    with open("../jsonpath-compliance-test-suite/cts.json") as fd:
        data = json.load(fd)

    return [
        (CTSCase(t["selector"], t["document"]))
        for t in data["tests"]
        if not t.get("invalid_selector", False)
    ]


QUERIES = valid_queries()

COMPILE_AND_FIND_STMT = """\
for path, data in QUERIES:
    list(find(path, data))"""

COMPILE_AND_FIND_VALUES_STMT = """\
for path, data in QUERIES:
    [node.value for node in find(path, data)]"""

JUST_PARSE_STMT = """\
for path, _ in QUERIES:
    PARSER.parse("jsonpath", path)"""

JUST_COMPILE_STMT = """\
for path, _ in QUERIES:
    compile(path)"""

JUST_FIND_SETUP = """\
compiled_queries = [(compile(q), d) for q, d in QUERIES]
"""

JUST_FIND_STMT = """\
for path, data in compiled_queries:
    list(path.find(data))"""

JUST_FIND_VALUES_STMT = """\
for path, data in compiled_queries:
    [node.value for node in path.find(data)]"""


def benchmark(number: int = 10, best_of: int = 3) -> None:
    print(f"repeating {len(QUERIES)} queries {number} times, best of {best_of} rounds")

    results = timeit.repeat(
        COMPILE_AND_FIND_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": JP_PARSER,
            "find": find,
            "compile": compile,
        },
        number=number,
        repeat=best_of,
    )

    print("compile and find".ljust(30), f"\033[92m{min(results):.3f}\033[0m")

    results = timeit.repeat(
        COMPILE_AND_FIND_VALUES_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": JP_PARSER,
            "find": find,
            "compile": compile,
        },
        number=number,
        repeat=best_of,
    )

    print("compile and find (values)".ljust(30), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_PARSE_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": PARSER,
            "find": find,
            "compile": compile,
        },
        number=number,
        repeat=best_of,
    )

    print("just pest parse".ljust(30), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_COMPILE_STMT,
        globals={
            "QUERIES": QUERIES,
            "PARSER": JP_PARSER,
            "find": find,
            "compile": compile,
        },
        number=number,
        repeat=best_of,
    )

    print("just compile".ljust(30), f"{min(results):.3f}")

    results = timeit.repeat(
        JUST_FIND_STMT,
        setup=JUST_FIND_SETUP,
        globals={
            "QUERIES": QUERIES,
            "PARSER": JP_PARSER,
            "find": find,
            "compile": compile,
        },
        number=number,
        repeat=best_of,
    )

    print("just find".ljust(30), f"\033[92m{min(results):.3f}\033[0m")

    results = timeit.repeat(
        JUST_FIND_VALUES_STMT,
        setup=JUST_FIND_SETUP,
        globals={
            "QUERIES": QUERIES,
            "PARSER": JP_PARSER,
            "find": find,
            "compile": compile,
        },
        number=number,
        repeat=best_of,
    )

    print("just find (values)".ljust(30), f"{min(results):.3f}")


if __name__ == "__main__":
    benchmark()
