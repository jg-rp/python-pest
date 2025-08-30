from pest.scanner import tokenize

with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    grammar = fd.read()

tokens = tokenize(grammar)

for token in tokens:
    print(token)
