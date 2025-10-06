import json

from pest import Parser

with open("tests/grammars/reporting.pest") as fd:
    GRAMMAR = fd.read()

parser = Parser.from_grammar(GRAMMAR, optimizer=None)

# print(parser.tree_view())

with open("tmp.py", "w") as fd:
    fd.write(parser.generate())


from tmp import Rule
from tmp import parse

pairs = parse(Rule.CHOICES, "x")
print(json.dumps(pairs.as_list(), indent=2))
