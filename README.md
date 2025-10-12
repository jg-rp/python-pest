# pest for Python

TODO

## Pest parser vs hand-crafted parsers

When writing a hand-crafted parser we might start with a lexer (aka scanner aka lexical scanner). The lexer is responsible for scanning input text and producing tokens, which we must choose and define by hand. A parser then consumes tokens produced by the lexer and builds an abstract syntax tree.

```
Lexer -> Tokens -> Parser -> AST ..
```

When using pest we start by writing a grammar. That grammar is used by pest to build a parse tree from input text. Each non-silent rule in the grammar becomes a pair of tokens in the parse tree. It is then up to us to parse those token pairs into an abstract syntax tree.

```
Grammar -> Parse Tree -> Parser -> AST ..
```

Pest parse trees are usually more structured than a flat sequence of tokens. They model the structure of the grammar making it easier to reason about...

## Parsing grammars with operator precedence (WIP)

`examples/calculator/grammar_encoded_prec.py` is an example of parsing a grammar with precedence represented directly in the grammar.

`examples/calculator/prec_climber.py` is an example of parsing a grammar using the precedence climbing technique, a kind of recursive descent parser.

`examples/calculator/pratt.py` is an example of parsing a grammar using a Pratt parser, which is also a recursive descent parser, but more extensible/composable than the precedence climbing technique.
