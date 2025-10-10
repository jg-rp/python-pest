from ._types import JSONValue
from .jsonpath import JSONPathParser
from .node import JSONPathNodeList
from .query import JSONPathQuery

__all__ = (
    "JSONValue",
    "JSONPathParser",
    "JSONPathNodeList",
    "JSONPathQuery",
    "find",
    "compile",
)

DEFAULT_PARSER = JSONPathParser()


def find(query: str, data: JSONValue) -> JSONPathNodeList:
    return DEFAULT_PARSER.parse(query).find(data)


def compile(query: str) -> JSONPathQuery:
    return DEFAULT_PARSER.parse(query)
