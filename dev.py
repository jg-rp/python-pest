from pest import Parser

with open("examples/calculator/calculator.pest") as fd:
    GRAMMAR = fd.read()

parser = Parser.from_grammar(GRAMMAR)

with open("tmp.py", "w") as fd:
    fd.write(parser.generate())


# from tmp import parse
# from tmp import Rule

# pairs = parse(Rule.NEGATIVE, "x")
# print(pairs.dumps())

# TODO: refactor `Expression.parse`
# TODO: revisit parse error context and messages
# TODO: CLI for generating parsers from grammar
