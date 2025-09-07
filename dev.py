import json

from pest import Parser

with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)

print(parser)

# with open("tests/examples/example.toml", encoding="utf-8") as fd:
#     example = fd.read()

# pairs = parser.parse("toml", example)

# print(json.dumps(pairs.as_list(), indent=2))
