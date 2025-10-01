from pest import Parser
from pest.grammar.codegen.generate import generate_module

with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    grammar = fd.read()

g = Parser.from_grammar(grammar, optimizer=None)
# rules = Parser.from_grammar(grammar).rules

# TODO: Attach rule tags in generated code
# TODO: generate_module
#    - Prelude
#       - modifier bit masks


print(generate_module(g.rules))

# print(g.tree_view())

# from pest.grammar.codegen.state import State
# from tmp import parse_header

# t = "Connection: keep-alive\n"
# state = State(t)
# pairs = parse_header(state)
# print(pairs.as_list())
