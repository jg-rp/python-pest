from pest import Parser

with open("tests/grammars/json.pest") as fd:
    GRAMMAR = fd.read()

parser = Parser.from_grammar(GRAMMAR, optimizer=None)
pairs = parser.parse("array", "[ ]")

print(pairs.dumps(compact=False))

# from tmp import parse
# from tmp import Rule

# pairs = parse(Rule.NEGATIVE, "x")
# print(pairs.dumps())

# TODO: revisit parse error context and messages
# TODO: CLI for generating parsers from grammar
