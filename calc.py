from pest import Parser

# Read grammar rules from a file.
with open("calculator.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)
parse_tree = parser.parse("program", "1 + 2")

print(parse_tree.dumps())
print(parse_tree.dumps(compact=False))
