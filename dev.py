from pest.parser import Parser
from pest.scanner import tokenize

with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
    source = fd.read()

tokens = tokenize(source)
parser = Parser(tokens)
grammar = parser.parse()

print(grammar)
