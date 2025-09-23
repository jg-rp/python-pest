import json
from enum import StrEnum
from enum import auto
from typing import TYPE_CHECKING

from pest import Pair
from pest import Parser

from ._ast import FilterSelector
from ._ast import IndexSelector
from ._ast import JSONPathChildSegment
from ._ast import JSONPathRecursiveDescentSegment
from ._ast import JSONPathSegment
from ._ast import JSONPathSelector
from ._ast import NameSelector
from ._ast import SliceSelector
from ._ast import WildcardSelector
from .exceptions import JSONPathSyntaxError
from .filter_expression import Expression
from .filter_expression import FilterExpression
from .filter_expression import LogicalExpression
from .query import JSONPathQuery

with open("examples/jsonpath/jsonpath.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)

pairs = parser.parse("jsonpath", "$['foo', 99].bar[0]")

print(json.dumps(pairs.as_list(), indent=2))


class Rule(StrEnum):
    JSONPATH = auto()
    CHILD_SEGMENT = auto()
    DESCENDANT_SEGMENT = auto()
    BRACKETED_SELECTION = auto()
    WILDCARD_SELECTOR = auto()
    MEMBER_NAME_SHORTHAND = auto()
    DOUBLE_QUOTED = auto()
    SINGLE_QUOTED = auto()
    SLICE_SELECTOR = auto()
    INDEX_SELECTOR = auto()
    FILTER_SELECTOR = auto()


# print(parser.tree_view())


class JSONPathParser:
    def parse(self, query: str) -> JSONPathQuery:
        segments = parser.parse(Rule.JSONPATH, query)
        return JSONPathQuery([self.parse_segment(pair) for pair in segments])

    def parse_segment(self, segment: Pair) -> JSONPathSegment:
        match segment:
            case Pair(Rule.CHILD_SEGMENT, [inner]):
                return JSONPathChildSegment(segment, self.parse_segment_inner(inner))
            case Pair(Rule.DESCENDANT_SEGMENT, [inner]):
                return JSONPathRecursiveDescentSegment(
                    segment, self.parse_segment_inner(inner)
                )
            case _:
                raise JSONPathSyntaxError("expected a segment", segment)

    def parse_segment_inner(self, inner: Pair) -> list[JSONPathSelector]:
        match inner:
            case Pair(Rule.BRACKETED_SELECTION, selectors):
                return [self.parse_selector(selector) for selector in selectors]
            case Pair(Rule.WILDCARD_SELECTOR):
                return [WildcardSelector(inner)]
            case Pair(Rule.MEMBER_NAME_SHORTHAND):
                return [NameSelector(inner, inner.text)]
            case _:
                raise JSONPathSyntaxError(
                    "expected a shorthand selector or bracketed selection", inner
                )

    def parse_selector(self, selector: Pair) -> JSONPathSelector:
        match selector:
            case Pair(Rule.DOUBLE_QUOTED):
                return NameSelector(selector, selector.text)  # TODO: unescape
            case Pair(Rule.SINGLE_QUOTED):
                # TODO: unescape
                return NameSelector(selector, selector.text.replace("\\'", "'"))
            case Pair(Rule.WILDCARD_SELECTOR):
                return WildcardSelector(selector)
            case Pair(Rule.SLICE_SELECTOR, inner):
                return SliceSelector(selector, *(int(str(i)) for i in inner))
            case Pair(Rule.INDEX_SELECTOR):
                return IndexSelector(selector, int(str(selector)))
            case Pair(Rule.FILTER_SELECTOR, [expression]):
                return FilterSelector(
                    selector,
                    FilterExpression(
                        selector, self.parse_logical_or_expression(expression)
                    ),
                )
            case Pair(Rule.MEMBER_NAME_SHORTHAND):
                return NameSelector(selector, str(selector))
            case _:
                raise JSONPathSyntaxError("expected a selector", selector)

    def parse_logical_or_expression(self, expression: Pair) -> Expression:
        it = iter(expression)
        or_expr: Expression = self.parse_logical_and_expression(next(it))
        for expr in it:
            right = self.parse_logical_and_expression(expr)
            or_expr = LogicalExpression(expr, or_expr, "||", right)
        return or_expr

    def parse_logical_and_expression(self, expression: Pair) -> Expression:
        raise NotImplementedError
