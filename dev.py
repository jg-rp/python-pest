from pest import DEFAULT_OPTIMIZER_PASSES
from pest import Optimizer
from pest import Parser
from pest.grammar import parse

rules, _ = parse('rule = { "a"{,3} }', Parser.BUILTIN)
# rules, _ = parse("rule = { (!NEWLINE ~ ANY)* }", Parser.BUILTIN)

print(rules["rule"].expression.tree_view())

optimizer = Optimizer(DEFAULT_OPTIMIZER_PASSES)
optimized = optimizer.optimize(rules, debug=True)

print("")
for entry in optimizer.log:
    print(entry)

print("")
print(rules["rule"].expression.tree_view())
