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
        # TODO: built-in rules

    def __str__(self) -> str:
        doc = (
            "".join(f"//!{token.value}\n" for token in self.doc) + "\n"
            if self.doc
            else ""
        )

        return doc + "\n\n".join(str(rule) for rule in self.rules.values())
