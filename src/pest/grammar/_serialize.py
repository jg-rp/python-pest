import json

from . import _ast
from ._ast import Expression
from ._modifiers import modifier_to_str


def serialize_expression(expression: Expression) -> str:
    match expression:
        case (_ast.IDENT, _, tag, name):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}{name}"

        case (_ast.RULE, _, name, expr, modifier, doc):
            doc_ = "".join(f"///{line}\n" for line in doc) if doc else ""
            modifier_ = modifier_to_str(modifier)
            return f"{doc_}{name} = {modifier_}{{ {serialize_expression(expr)} }}"

        case (_ast.CHOICE, _, left, right):
            return f"{serialize_expression(left)} | {serialize_expression(right)}"

        case (_ast.SEQUENCE, _, left, right):
            return f"{serialize_expression(left)} ~ {serialize_expression(right)}"

        case (_ast.GROUP, _, tag, expr):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}({serialize_expression(expr)})"

        case (_ast.POSITIVE_PREDICATE, _, tag, expr):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}&{serialize_expression(expr)}"

        case (_ast.NEGATIVE_PREDICATE, _, tag, expr):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}!{serialize_expression(expr)}"

        case (_ast.OPTIONAL, _, expr):
            return f"{serialize_expression(expr)}?"

        case (_ast.REPEAT, _, expr):
            return f"{serialize_expression(expr)}*"

        case (_ast.REPEAT_ONCE, _, expr):
            return f"{serialize_expression(expr)}+"

        case (_ast.REPEAT_EXACT, _, expr, n):
            return f"{serialize_expression(expr)}{{{n}}}"

        case (_ast.REPEAT_MIN, _, expr, n):
            return f"{serialize_expression(expr)}{{{n},}}"

        case (_ast.REPEAT_MAX, _, expr, n):
            return f"{serialize_expression(expr)}{{,{n}}}"

        case (_ast.REPEAT_MIN_MAX, _, expr, n, m):
            return f"{serialize_expression(expr)}{{{n},{m}}}"

        case (_ast.PUSH_LITERAL, _, tag, value):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}PUSH({json.dumps(value)})"

        case (_ast.PUSH, _, tag, expr):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}PUSH( {serialize_expression(expr)} )"

        case (_ast.PEEK_SLICE, _, tag, start, stop):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}PEEK[{start or ''}..{stop or ''}]"

        case (_ast.PEEK, _, tag):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}PEEK"

        case (_ast.PEEK_ALL, _, tag):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}PEEK_ALL"

        case (_ast.POP, _, tag):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}POP"

        case (_ast.POP_ALL, _, tag):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}POP_ALL"

        case (_ast.DROP, _, tag):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}DROP"

        case (_ast.STRING, _, value):
            return json.dumps(value)

        case (_ast.CI_STRING, _, value):
            return f"^{json.dumps(value)}"

        case (_ast.RANGE, _, tag, start, stop):
            tag_ = f"#{tag}=" if tag else ""
            return f"{tag_}{start!r}..{stop!r}"

        case (_ast.REGEX, _, pattern):
            return f"`{pattern}`"

        case (_ast.SOI, _, _):
            return "SOI"

        case (_ast.EOI, _, _):
            return "EOI"

        case (_ast.ANY, _, _):
            return "ANY"
