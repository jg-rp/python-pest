from .jsonpath import JSONPathParser
from .node import JSONPathNodeList
from .query import JSONPathQuery
from .types import JSONValue

# TODO: Finish me

PARSER = JSONPathParser()


def find(query: str, data: JSONValue) -> JSONPathNodeList:
    return PARSER.parse(query).find(data)


def compile(query: str) -> JSONPathQuery:
    return PARSER.parse(query)
