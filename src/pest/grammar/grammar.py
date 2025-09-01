"""A pest grammar."""

from .expressions import Rule


class Grammar:
    """A pest grammar.

    Attributes:
        rules: A mapping of rule names to `Rule` instances.
        doc: An optional list of `GRAMMAR_DOC` lines.
    """

    __slots__ = ("rules", "doc")

    def __init__(self, rules: dict[str, Rule], doc: list[str] | None = None):
        self.rules = rules
        self.doc = doc
        # TODO: built-in rules

    def __str__(self) -> str:
        doc = "".join(f"//!{line}\n" for line in self.doc) + "\n" if self.doc else ""
        return doc + "\n\n".join(str(rule) for rule in self.rules.values())
