from pest import Parser

with open("examples/jsonpath/jsonpath.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)

print(parser.tree_view())
