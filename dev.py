import json

from pest import DEFAULT_OPTIMIZER_PASSES
from pest import Optimizer
from pest import Parser
from pest.grammar import parse

# rules, _ = parse('rule = { (!"\n" ~ ANY)* }', Parser.BUILTIN)

# print(rules["rule"].expression.tree_view())

# optimizer = Optimizer(DEFAULT_OPTIMIZER_PASSES)
# optimized = optimizer.optimize(rules, debug=True)

# print("")
# for entry in optimizer.log:
#     print(entry)

# print("")
# print(rules["rule"].expression.tree_view())


with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)
pairs = parser.parse("repeat_max_atomic", "abcabcabc")
print(json.dumps(pairs.as_list(), indent=2))
