"""A translation of the INI example found in the pest book.

https://pest.rs/book/examples/ini.html
"""

import json
from collections import defaultdict

from pest import Parser

with open("examples/ini/ini.pest") as fd:
    grammar = fd.read()

with open("examples/ini/example.ini", encoding="ascii") as fd:
    file = fd.read()

parser = Parser.from_grammar(grammar, optimizer=None)

# The name of the rule to start from and the input string to parse.
pairs = parser.parse("file", file)

properties: defaultdict[str, dict[str, str]] = defaultdict(dict)
current_section_name = ""

for pair in next(iter(pairs)):
    if pair.name == "section":
        current_section_name = str(next(iter(pair.inner())))
    elif pair.name == "property":
        inner_rules = iter(pair.inner())  # { name ~ "=" ~ value }
        name = str(next(inner_rules))
        value = str(next(inner_rules))
        section = properties[current_section_name][name] = value
    elif pair.name == "EOI":
        break
    else:
        raise Exception(f"unexpected rule {pair.name!r}")


print(json.dumps(dict(properties), indent=2))
