from enum import StrEnum


class Rule(StrEnum):
    """Grammar rules."""

    EOI = "EOI"
    WHITESPACE = "WHITESPACE"
    PROGRAM = "program"
    EXPR = "expr"
    ADD_SUB = "add_sub"
    ADD_OP = "add_op"
    ADD = "add"
    SUB = "sub"
    MUL_DIV = "mul_div"
    MUL_OP = "mul_op"
    MUL = "mul"
    DIV = "div"
    POW_EXPR = "pow_expr"
    POW_OP = "pow_op"
    POW = "pow"
    PREFIX = "prefix"
    NEG = "neg"
    POSTFIX = "postfix"
    FAC = "fac"
    PRIMARY = "primary"
    INT = "int"
    IDENT = "ident"
