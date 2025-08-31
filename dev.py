from pest.scanner import tokenize
from pest.parser import Parser

with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    source = fd.read()

tokens = tokenize(source)
parser = Parser(tokens)
grammar = parser.parse()
