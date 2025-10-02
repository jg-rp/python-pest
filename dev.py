from pest import Parser

with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
    grammar = fd.read()

with open("tmp.py", "w") as fd:
    fd.write(Parser.from_grammar(grammar).generate())

# rules = Parser.from_grammar(grammar).rules

# TODO: Attach rule tags in generated code
# TODO: generate_module
#    - Prelude
#       - modifier bit masks


# print(g.tree_view())

# import json
# from pest.grammar.codegen.state import State
# from tmp import parse_partial_time

# t = "12:34:56.000"
# state = State(t)
# pairs = parse_partial_time(state)
# print(json.dumps(pairs.as_list(), indent=2))
