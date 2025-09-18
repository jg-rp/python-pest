import json

from pest import DEFAULT_OPTIMIZER_PASSES
from pest import DUMMY_OPTIMIZER
from pest import Optimizer
from pest import Parser
from pest.grammar import parse

# rules, _ = parse('string = { "abc" }\nrule = { string{, 2} }', Parser.BUILTIN)

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

parser = Parser.from_grammar(grammar, optimizer=DUMMY_OPTIMIZER)
pairs = parser.parse("repeat_max", "abc abc abc")
print(json.dumps(pairs.as_list(), indent=2))
