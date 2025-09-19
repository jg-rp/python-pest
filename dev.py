import json

from pest import DEFAULT_OPTIMIZER_PASSES
from pest import Optimizer
from pest import Parser
from pest.grammar import parse

# grammar = """\
# identifier = { (ASCII_ALPHANUMERIC | "_" | "-")+ }"""

with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
    grammar = fd.read()

rules, _ = parse(grammar, Parser.BUILTIN)

rule = "unicode"
print(rules[rule].expression.tree_view())

optimizer = Optimizer(DEFAULT_OPTIMIZER_PASSES)
optimized = optimizer.optimize(rules, debug=True)

print("")
for entry in optimizer.log:
    print(entry)

print("")
print(optimized[rule].expression.tree_view())


# with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
#     grammar = fd.read()

# parser = Parser.from_grammar(grammar)
# pairs = parser.parse("repeat_max_atomic", "abcabcabc")
# print(json.dumps(pairs.as_list(), indent=2))
