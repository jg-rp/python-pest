import json

from pest import Pairs
from pest import Parser

GRAMMAR = """\
expr = { "a" | "b" | c }
c = _{ "c" }
"""

parser = Parser.from_grammar(GRAMMAR, optimizer=None)

print(parser.tree_view())

with open("tmp.py", "w") as fd:
    fd.write(parser.generate())

from tmp import parse_expr
from pest.grammar.codegen.state import State

pairs = parse_expr(State("b"))
print(json.dumps(pairs.as_list(), indent=2))

# TODO: Attach rule tags in generated code
# TODO: Tidy generated comments that delimit expressions.
# TODO: include expression name in delimit comments
# TODO: Introduce SilentBuiltInRule and move all but EOI to it
