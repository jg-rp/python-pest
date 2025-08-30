"""A pest grammar."""

from .expressions import Rule
from .tokens import Token


class Grammar:
    """A pest grammar.

    Attributes:
        rules: A mapping of rule names to `Rule` instances.
        doc: An optional list of tokens of kind `GRAMMAR_DOC`.
    """

    __slots__ = ("rules", "doc")

    def __init__(self, rules: dict[str, Rule], doc: list[Token] | None = None):
        self.rules = rules
        self.doc = doc
