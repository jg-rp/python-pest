from . import _ast
from ._ast import Expression
from ._serialize import serialize_expression

NODE_NAMES = [
    "",
    "Choice",
    "Group",
    "Optional",
    "Repeat",
    "RepeatOnce",
    "RepeatExact",
    "RepeatMin",
    "RepeatMax",
    "RepeatMinMax",
    "PositivePredicate",
    "NegativePredicate",
    "Sequence",
    "PushLiteral",
    "Push",
    "PeekSlice",
    "Peek",
    "PeekAll",
    "Pop",
    "PopAll",
    "Drop",
    "Ident",
    "String",
    "CIString",
    "Range",
    "Rule",
    "Regex",
    "StartOfInput",
    "EndOfInput",
    "Any",
]


def tree_view(expression: Expression) -> str:
    """Return an ASCII tree view of `expression` and its children."""
    # (prefix, connector, class_name, repr_value)
    nodes: list[tuple[str, str, str, str]] = []

    def collect(
        node: Expression,
        prefix: str = "",
        *,
        is_last: bool = True,
    ) -> None:
        connector = "" if prefix == "" else ("└── " if is_last else "├── ")

        nodes.append(
            (
                prefix,
                connector,
                NODE_NAMES[node[0]],
                repr(serialize_expression(node)),
            )
        )

        child_prefix = prefix + ("    " if is_last else "│   ")
        children = _children(node)

        for i, child in enumerate(children):
            last = i == len(children) - 1
            collect(child, child_prefix, is_last=last)

    collect(expression)

    # Find maximum width of the left-hand side
    widths = [len(prefix + connector + cls) for prefix, connector, cls, _ in nodes]
    max_width = max(widths) if widths else 0

    # Build aligned lines
    lines: list[str] = []
    for (prefix, connector, cls, val), width in zip(nodes, widths, strict=True):
        left = prefix + connector + cls
        padding = " " * (max_width - width + 4)  # +4 for spacing column
        lines.append(left + padding + val)

    return "\n".join(lines)


def _children(expression: Expression) -> list[Expression]:
    match expression:
        case (_ast.IDENT | _ast.PUSH_LITERAL, _, _, _):
            return []

        case (_ast.RULE, _, _, expr, _, _):
            return [expr]

        case (_ast.CHOICE | _ast.SEQUENCE, _, expressions):
            return list(expressions)

        case (
            _ast.GROUP | _ast.POSITIVE_PREDICATE | _ast.NEGATIVE_PREDICATE,
            _,
            _,
            expr,
        ):
            return [expr]

        case (_ast.OPTIONAL | _ast.REPEAT | _ast.REPEAT_ONCE, _, expr):
            return [expr]

        case (_ast.REPEAT_EXACT | _ast.REPEAT_MIN | _ast.REPEAT_MAX, _, expr, _):
            return [expr]

        case (_ast.REPEAT_MIN_MAX, _, expr, _, _):
            return [expr]

        case (_ast.PUSH, _, _, expr):
            return [expr]

        case (_ast.PEEK_SLICE | _ast.RANGE, _, _, _, _):
            return []

        case (
            _ast.PEEK
            | _ast.PEEK_ALL
            | _ast.POP
            | _ast.POP_ALL
            | _ast.DROP
            | _ast.STRING
            | _ast.CI_STRING
            | _ast.REGEX
            | _ast.SOI
            | _ast.EOI
            | _ast.ANY,
            _,
            _,
        ):
            return []
