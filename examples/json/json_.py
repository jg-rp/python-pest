"""A translation of the JSON example found in the pest book.

https://pest.rs/book/examples/json.html

NOTE: If running this from the root of the Python pest source tree, use
`python -m examples.json.json_` to work around relative import issues.
"""

from enum import StrEnum  # Requires Python 3.11+
from enum import auto

from pest import Pair
from pest import Parser

from ._ast import JSONArray
from ._ast import JSONBool
from ._ast import JSONNull
from ._ast import JSONNumber
from ._ast import JSONObject
from ._ast import JSONString
from ._ast import JSONValue

with open("examples/json/json.pest") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)


class Rule(StrEnum):
    """Rule names for our grammar."""

    JSON = auto()
    OBJECT = auto()
    ARRAY = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()


def parse_json_file(data: str) -> JSONValue:
    """Parse JSON data using a pest grammar."""
    json_ = parser.parse(Rule.JSON, data).first()
    return parse_json_value(json_)


def parse_json_value(pair: Pair) -> JSONValue:
    match pair:
        case Pair(Rule.OBJECT, pairs):
            return JSONObject(
                [
                    (
                        k.inner().first().text,
                        parse_json_value(v),
                    )
                    for k, v in pairs
                ]
            )
        case Pair(Rule.ARRAY, inner):
            return JSONArray([parse_json_value(v) for v in inner])
        case Pair(Rule.STRING, [inner]):
            return JSONString(inner.text)
        case Pair(Rule.NUMBER):
            return JSONNumber(float(pair.text))
        case Pair(Rule.BOOLEAN):
            return JSONBool(pair.text == "true")
        case Pair(Rule.NULL):
            return JSONNull()
        case _:
            raise Exception(f"unexpected rule {pair.name!r}")


if __name__ == "__main__":
    with open("examples/json/example.json", encoding="utf-8") as fd:
        unparsed_file = fd.read()

    json_ = parse_json_file(unparsed_file)
    print(json_.dumps())
