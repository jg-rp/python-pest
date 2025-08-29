from .rule import Rule
from .tokens import Token


class Grammar:
    """"""

    __slots__ = ("rules", "doc")

    def __init__(self, rules: list[Rule], doc: list[Token] | None = None):
        self.rules = rules
        self.doc = doc
