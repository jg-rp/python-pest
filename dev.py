import json

from pest import Pairs
from pest import Parser

# with open("tests/grammars/lists.pest") as fd:
#     GRAMMAR = fd.read()

# parser = Parser.from_grammar(GRAMMAR, optimizer=None)

# # print(parser.tree_view())

# with open("tmp.py", "w") as fd:
#     fd.write(parser.generate())

from tmp import parse

pairs = parse("lists", "- a\n- b")
print(json.dumps(pairs.as_list(), indent=2))

# TODO: Tidy generated comments that delimit expressions.
# TODO: include expression name in delimit comments
# TODO: Introduce SilentBuiltInRule and move all but EOI to it
