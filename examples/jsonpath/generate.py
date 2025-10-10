from pest import Parser

with open("examples/jsonpath/jsonpath.pest", encoding="utf-8") as fd:
    grammar = Parser.from_grammar(fd.read())

with open("examples/jsonpath/parser.py", "w", encoding="utf-8") as fd:
    fd.write(grammar.generate())
