"""A translation of the INI example found in the pest book.

https://pest.rs/book/examples/ini.html
"""

import json
from collections import defaultdict
from enum import StrEnum  # Requires Python 3.11+
from enum import auto

from pest import Pair
from pest import Parser

with open("examples/ini/ini.pest") as fd:
    grammar = fd.read()

with open("examples/ini/example.ini", encoding="ascii") as fd:
    unparsed_file = fd.read()

parser = Parser.from_grammar(grammar)


# Optionally enumerate your grammar rules manually for better type checking and
# autocomplete. We might add a codegen step to generate this automatically in
# the future.
class Rule(StrEnum):
    """Rule names for our grammar."""

    FILE = auto()
    SECTION = auto()
    PROPERTY = auto()
    EOI = "EOI"


# Raises a `PestParsingError` if `unparsed_file` fails to parse.
file = parser.parse(Rule.FILE, unparsed_file).first()

properties: defaultdict[str, dict[str, str]] = defaultdict(dict)
current_section_name = ""

for pair in file:
    match pair:
        case Pair(Rule.SECTION, [name]):  # { name }
            current_section_name = name.text
        case Pair(Rule.PROPERTY, [name, value]):  # { name ~ "=" ~ value }
            properties[current_section_name][name.text] = value.text
        case Pair(Rule.EOI):
            break
        case _:
            raise Exception(f"unexpected rule {pair.name!r}")


print(json.dumps(dict(properties), indent=2))
