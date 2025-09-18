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


# with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
#     grammar = fd.read()

# parser = Parser.from_grammar(grammar, optimizer=DUMMY_OPTIMIZER)
# pairs = parser.parse("repeat_max_atomic", "abcabcabc")
# print(json.dumps(pairs.as_list(), indent=2))

from pest.grammar.expressions.choice import ChoiceCase
from pest.grammar.expressions.choice import LazyChoiceRegex
from pest.grammar.expressions.choice import _Choice  # noqa: F401
from pest.grammar.expressions.choice import build_optimized_pattern
from pest.grammar.rules.unicode import UnicodePropertyRule


greek = UnicodePropertyRule("\\p{Script=Greek}", "MOCK_PROP")
choices: list[_Choice] = [
    ("abc", ChoiceCase.SENSITIVE),
    ("x", ChoiceCase.INSENSITIVE),
    ("0", "9"),
    greek,
]
pattern = build_optimized_pattern(choices)
print(pattern)
