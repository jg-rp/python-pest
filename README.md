# pest for Python

TODO

## Parsing grammars with operator precedence (WIP)

`examples/jsonpath/` is an example of parsing a grammar with precedence represented directly in the grammar.

`examples/calculator/` is an example of parsing a grammar using the precedence climbing technique, a kind of recursive descent parser.

`examples/calculator_pratt/` is an example of parsing a grammar using a Pratt parser, which is also a recursive descent parser, but more extensible/composable than the precedence climbing technique.
