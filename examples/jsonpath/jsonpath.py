"""JSONPath query expression parser."""

from __future__ import annotations

from enum import StrEnum
from enum import auto
from typing import TYPE_CHECKING

from pest import Pair
from pest import Parser

from ._ast import ChildSegment
from ._ast import FilterSelector
from ._ast import IndexSelector
from ._ast import NameSelector
from ._ast import RecursiveDescentSegment
from ._ast import Segment
from ._ast import Selector
from ._ast import SliceSelector
from ._ast import WildcardSelector
from .exceptions import JSONPathSyntaxError
from .filter_expression import BooleanLiteral
from .filter_expression import ComparisonExpression
from .filter_expression import Expression
from .filter_expression import FilterExpression
from .filter_expression import FloatLiteral
from .filter_expression import FunctionExtension
from .filter_expression import IntegerLiteral
from .filter_expression import LogicalExpression
from .filter_expression import NullLiteral
from .filter_expression import PrefixExpression
from .filter_expression import RelativeFilterQuery
from .filter_expression import RootFilterQuery
from .filter_expression import StringLiteral
from .function_extensions import Count
from .function_extensions import Length
from .function_extensions import Match
from .function_extensions import Search
from .function_extensions import Value
from .query import JSONPathQuery

if TYPE_CHECKING:
    from .function_extensions import FilterFunction

with open("examples/jsonpath/jsonpath.pest", encoding="utf-8") as fd:
    grammar = fd.read()

PARSER = Parser.from_grammar(grammar)


class Rule(StrEnum):
    """JSONPath grammar rules."""

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
    PAREN_EXPR = auto()
    COMPARISON_EXPR = auto()
    TEST_EXPR = auto()
    NUMBER = auto()
    TRUE_LITERAL = auto()
    FALSE_LITERAL = auto()
    NULL = auto()
    REL_SINGULAR_QUERY = auto()
    ABS_SINGULAR_QUERY = auto()
    FUNCTION_EXPR = auto()
    INT = auto()
    FRAC = auto()
    EXP = auto()
    LOGICAL_OR_EXPR = auto()
    LOGICAL_AND_EXPR = auto()
    REL_QUERY = auto()
    ROOT_QUERY = auto()
    NAME_SEGMENT = auto()
    INDEX_SEGMENT = auto()


class JSONPathParser:
    """JSONPath query expression parser."""

    FUNCTION_EXTENSIONS: dict[str, FilterFunction] = {
        "count": Count(),
        "length": Length(),
        "match": Match(),
        "search": Search(),
        "value": Value(),
    }

    def parse(self, query: str) -> JSONPathQuery:
        segments = PARSER.parse(Rule.JSONPATH, query)
        return JSONPathQuery(
            [self.parse_segment(pair) for pair in segments if pair.name != "EOI"]
        )

    def parse_segment(self, segment: Pair) -> Segment:
        match segment:
            case Pair(Rule.CHILD_SEGMENT, [inner]):
                return ChildSegment(segment, self.parse_segment_inner(inner))
            case Pair(Rule.DESCENDANT_SEGMENT, [inner]):
                return RecursiveDescentSegment(segment, self.parse_segment_inner(inner))
            case Pair(Rule.NAME_SEGMENT, [inner]) | Pair(Rule.INDEX_SEGMENT, [inner]):
                return ChildSegment(segment, [self.parse_selector(inner)])
            case _:
                raise JSONPathSyntaxError("expected a segment", segment)

    def parse_segment_inner(self, inner: Pair) -> list[Selector]:
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

    def parse_selector(self, selector: Pair) -> Selector:
        match selector:
            case Pair(Rule.DOUBLE_QUOTED):
                # TODO: unescape
                return NameSelector(selector, selector.text)
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
        it = iter(expression)
        and_expr: Expression = self.parse_basic_expression(next(it))
        for expr in it:
            right = self.parse_basic_expression(expr)
            and_expr = LogicalExpression(expr, and_expr, "&&", right)
        return and_expr

    def parse_basic_expression(self, expression: Pair) -> Expression:
        match expression:
            case Pair(Rule.PAREN_EXPR, [not_expr, or_expr]):
                return PrefixExpression(
                    not_expr,
                    "!",
                    self.parse_logical_or_expression(or_expr),
                )
            case Pair(Rule.PAREN_EXPR, [or_expr]):
                return self.parse_logical_or_expression(or_expr)
            case Pair(Rule.COMPARISON_EXPR, [left, op, right]):
                return ComparisonExpression(
                    expression,
                    self.parse_comparable(left),
                    op.text,
                    self.parse_comparable(right),
                )
            case Pair(Rule.TEST_EXPR, [not_expr, test_expr]):
                return PrefixExpression(
                    not_expr,
                    "!",
                    self.parse_test_expression(test_expr),
                )
            case Pair(Rule.TEST_EXPR, [test_expr]):
                return self.parse_test_expression(test_expr)
            case _:
                raise JSONPathSyntaxError("expected a basic expression", expression)

    def parse_test_expression(self, expression: Pair) -> Expression:
        match expression:
            case Pair(Rule.REL_QUERY, segments):
                return RelativeFilterQuery(
                    expression, JSONPathQuery([self.parse_segment(s) for s in segments])
                )
            case Pair(Rule.ROOT_QUERY, segments):
                return RootFilterQuery(
                    expression, JSONPathQuery([self.parse_segment(s) for s in segments])
                )
            case Pair(Rule.FUNCTION_EXPR, [name, *rest]):
                return FunctionExtension(
                    expression,
                    name.text,
                    [self.parse_function_argument(e) for e in rest],
                    self.FUNCTION_EXTENSIONS[name.text],
                )
            case _:
                raise JSONPathSyntaxError("expected a test expression", expression)

    def parse_comparable(self, expression: Pair) -> Expression:
        match expression:
            case Pair(Rule.NUMBER):
                return self.parse_number(expression)
            case Pair(Rule.DOUBLE_QUOTED):
                # TODO: unescape
                return StringLiteral(expression, expression.text)
            case Pair(Rule.SINGLE_QUOTED):
                # TODO: unescape
                return StringLiteral(expression, expression.text.replace("\\'", "'"))
            case Pair(Rule.TRUE_LITERAL):
                return BooleanLiteral(expression, value=True)
            case Pair(Rule.FALSE_LITERAL):
                return BooleanLiteral(expression, value=False)
            case Pair(Rule.NULL):
                return NullLiteral(expression, value=None)
            case Pair(Rule.REL_SINGULAR_QUERY, inner):
                return RelativeFilterQuery(
                    expression, JSONPathQuery([self.parse_segment(s) for s in inner])
                )
            case Pair(Rule.ABS_SINGULAR_QUERY, inner):
                return RootFilterQuery(
                    expression, JSONPathQuery([self.parse_segment(s) for s in inner])
                )
            case Pair(Rule.FUNCTION_EXPR, [name, *rest]):
                return FunctionExtension(
                    expression,
                    name.text,
                    [self.parse_function_argument(e) for e in rest],
                    self.FUNCTION_EXTENSIONS[name.text],
                )
            case _:
                raise JSONPathSyntaxError("expected a comparable", expression)

    def parse_number(self, expression: Pair) -> Expression:
        match expression:
            case Pair(Rule.NUMBER, []):
                return IntegerLiteral(expression, int(expression.text))
            case Pair(Rule.NUMBER, [Pair(Rule.INT)]):
                return IntegerLiteral(expression, int(expression.text))
            case Pair(Rule.NUMBER, [Pair(Rule.INT), Pair(Rule.FRAC)]):
                return FloatLiteral(expression, float(expression.text))
            case Pair(Rule.NUMBER, [Pair(Rule.INT), Pair(Rule.FRAC), Pair(Rule.EXP)]):
                return FloatLiteral(expression, float(expression.text))
            case Pair(Rule.NUMBER, [Pair(Rule.INT), Pair(Rule.EXP)]):
                if "-" in expression.children[-1].text:
                    return FloatLiteral(expression, float(expression.text))
                return IntegerLiteral(expression, int(float(expression.text)))
            case _:
                raise JSONPathSyntaxError("expected a number", expression)

    def parse_function_argument(self, expression: Pair) -> Expression:
        match expression:
            case Pair(Rule.NUMBER):
                return self.parse_number(expression)
            case Pair(Rule.DOUBLE_QUOTED):
                # TODO: unescape
                return StringLiteral(expression, expression.text)
            case Pair(Rule.SINGLE_QUOTED):
                # TODO: unescape
                return StringLiteral(expression, expression.text.replace("\\'", "'"))
            case Pair(Rule.TRUE_LITERAL):
                return BooleanLiteral(expression, value=True)
            case Pair(Rule.FALSE_LITERAL):
                return BooleanLiteral(expression, value=False)
            case Pair(Rule.NULL):
                return NullLiteral(expression, value=None)
            case Pair(Rule.REL_QUERY, inner):
                return RelativeFilterQuery(
                    expression, JSONPathQuery([self.parse_segment(s) for s in inner])
                )
            case Pair(Rule.ROOT_QUERY, inner):
                return RootFilterQuery(
                    expression, JSONPathQuery([self.parse_segment(s) for s in inner])
                )
            case Pair(Rule.FUNCTION_EXPR, [name, *rest]):
                return FunctionExtension(
                    expression,
                    name.text,
                    [self.parse_function_argument(e) for e in rest],
                    self.FUNCTION_EXTENSIONS[name.text],
                )
            case Pair(Rule.LOGICAL_OR_EXPR):
                return self.parse_logical_or_expression(expression)
            case Pair(Rule.LOGICAL_AND_EXPR):
                return self.parse_logical_and_expression(expression)
            case _:
                raise JSONPathSyntaxError("expected a function argument", expression)
