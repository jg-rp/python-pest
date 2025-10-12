from pest import Parser

with open("tests/grammars/reporting.pest") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)
parse_tree = parser.parse("mixed_progress", "b")

print(parse_tree.dumps())
