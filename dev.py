from python_pest.lexer import tokenize

with open("grammar.pest", encoding="utf-8") as fd:
    grammar = fd.read()

tokens = tokenize(grammar)

for token in tokens:
    print(token)
