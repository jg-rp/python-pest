import json

from pest import Parser

with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)

pairs = parser.parse("inline_table", "{ a = 'b' }")

print(json.dumps(pairs.as_list(), indent=2))
