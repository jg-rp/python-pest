from pest import Parser

with open("examples/calculator/calculator.pest") as fd:
    GRAMMAR = fd.read()

parser = Parser.from_grammar(GRAMMAR, optimizer=None)

# print(parser.tree_view())

pairs = parser.parse("program", "1 + 2 * 3 - (((2!)))")
print(pairs.dumps())

# TODO: refactor `Expression.parse`
# TODO: revisit parse error context and messages
# TODO: CLI for generating parsers from grammar
