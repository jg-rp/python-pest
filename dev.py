import json

from pest import DEFAULT_OPTIMIZER_PASSES
from pest import Optimizer
from pest import Parser
from pest import PestParsingError
from pest.grammar import parse

with open("tests/grammars/lists.pest", encoding="utf-8") as fd:
    grammar = fd.read()

# rules, _ = parse(grammar, Parser.BUILTIN)

# rule = "COMMENT"
# print(rules[rule].tree_view())

# optimizer = Optimizer(DEFAULT_OPTIMIZER_PASSES)
# optimized = optimizer.optimize(rules, debug=True)

# print("")
# for entry in optimizer.log:
#     print(entry)

# print("")
# print(optimized[rule].tree_view())


parser = Parser.from_grammar(grammar)
# try:
#     pairs = parser.parse(rule, "x")
# except PestParsingError as err:
#     print(f"positives: {err.positives}")
#     print(f"negatives: {err.negatives}")
#     raise
# print(json.dumps(pairs.as_list(), indent=2))


# with open("examples/ini/ini.pest") as fd:
#     grammar = fd.read()

# with open("examples/ini/example.ini", encoding="ascii") as fd:
#     unparsed_file = fd.read()

# parser = Parser.from_grammar(grammar, optimizer=None)

# print(parser.tree_view())


pairs = parser.parse("lists", "- a")

print(json.dumps(pairs.as_list(), indent=2))
