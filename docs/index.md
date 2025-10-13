# Python Pest

Python Pest is a port of the [Rust Pest](https://pest.rs/) parsing library - a powerful, elegant PEG (Parsing Expression Grammar) parser generator. We use exactly the same grammar syntax as Pest v2, so existing Pest grammars can be used without modification.

## Install

TODO:

## Example

### Grammar

This is the grammar for a simple calculator, copied from a [Rust pest example](https://github.com/pest-parser/pest/blob/master/derive/examples/calc.pest) ([license](https://github.com/pest-parser/pest/blob/master/LICENSE-MIT)) and modified to support variables.

```
program      =   { SOI ~ expr ~ EOI }
  expr       =   { prefix* ~ primary ~ postfix* ~ (infix ~ prefix* ~ primary ~ postfix* )* }
    infix    =  _{ add | sub | mul | div | pow }
      add    =   { "+" } // Addition
      sub    =   { "-" } // Subtraction
      mul    =   { "*" } // Multiplication
      div    =   { "/" } // Division
      pow    =   { "^" } // Exponentiation
    prefix   =  _{ neg }
      neg    =   { "-" } // Negation
    postfix  =  _{ fac }
      fac    =   { "!" } // Factorial
    primary  =  _{ int | "(" ~ expr ~ ")" | ident }
      int    =  @{ (ASCII_NONZERO_DIGIT ~ ASCII_DIGIT+ | ASCII_DIGIT) }
      ident  =  @{ ASCII_ALPHA+ }

WHITESPACE   =  _{ " " | "\t" | NEWLINE }
```

### Parse tree

To use a Pest grammar in Python we pass the grammar as a string to `Parser.from_grammar(grammar: str)` and get a `Parser` instance in return.

```python
from pest import Parser

# Read grammar rules from a file.
with open("calculator.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)
```

Instances of `Parser` have a `parse()` method that takes the name of the rule to start from and the input text to parse. Here we parse the expression `1 + 2` and dump the resulting parse tree to see how our grammar has parsed the input text.

```python
parse_tree = parser.parse("program", "1 + 2")
print(parse_tree.dumps())
# - program
#   - expr
#     - int: "1"
#     - add: "+"
#     - int: "2"
#   - EOI: ""
```

??? tip "Debug output"

    A more detailed parse tree representation is available by passing `compact=False` to `Pairs.dumps()`.

    ```python
    print(parse_tree.dumps(compact=False))
    ```

    ```json {title="JSON debug output"}
    [
      {
        "rule": "program",
        "span": {
          "str": "1 + 2",
          "start": 0,
          "end": 5
        },
        "inner": [
          {
            "rule": "expr",
            "span": {
              "str": "1 + 2",
              "start": 0,
              "end": 5
            },
            "inner": [
              {
                "rule": "int",
                "span": {
                  "str": "1",
                  "start": 0,
                  "end": 1
                },
                "inner": []
              },
              {
                "rule": "add",
                "span": {
                  "str": "+",
                  "start": 2,
                  "end": 3
                },
                "inner": []
              },
              {
                "rule": "int",
                "span": {
                  "str": "2",
                  "start": 4,
                  "end": 5
                },
                "inner": []
              }
            ]
          },
          {
            "rule": "EOI",
            "span": {
              "str": "",
              "start": 5,
              "end": 5
            },
            "inner": []
          }
        ]
      }
    ]
    ```

### Abstract syntax tree

Before processing a parse tree, we're going to define the nodes in our abstract syntax tree. In this example every node in the AST is an `Expression` with an `evaluate(variables) -> int` method. We evaluate a "program" by calling `evaluate()` on the root node of our AST.

```python
class Expression:
    """Base class for all expressions or sub expressions."""

    @abstractmethod
    def evaluate(self, variables: dict[str, int]) -> int:
        """Evaluate this expression."""
```

??? example "\_ast.py"

    We use `_ast.py` with an underscore so as not to conflict with the `ast` module in Python's standard library.

    ```python
    from abc import abstractmethod
    from collections.abc import Callable


    class Expression:
        """Base class for all expressions or sub expressions."""

        @abstractmethod
        def evaluate(self, variables: dict[str, int]) -> int:
            """Evaluate this expression."""


    class VarExpr(Expression):
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

        def evaluate(self, variables: dict[str, int]) -> int:
            return variables[self.value]


    class IntExpr(Expression):
        def __init__(self, value: int) -> None:
            super().__init__()
            self.value = value

        def evaluate(self, variables: dict[str, int]) -> int:
            return self.value


    class PrefixExpr(Expression):
        def __init__(self, op: Callable[[int], int], right: Expression) -> None:
            super().__init__()
            self.op = op
            self.right = right

        def evaluate(self, variables: dict[str, int]) -> int:
            return self.op(self.right.evaluate(variables))


    class InfixExpr(Expression):
        def __init__(
            self, op: Callable[[int, int], int], left: Expression, right: Expression
        ) -> None:
            super().__init__()
            self.op = op
            self.left = left
            self.right = right

        def evaluate(self, variables: dict[str, int]) -> int:
            return self.op(self.left.evaluate(variables), self.right.evaluate(variables))


    class PostfixExpr(Expression):
        def __init__(self, op: Callable[[int], int], expr: Expression) -> None:
            super().__init__()
            self.op = op
            self.expr = expr

        def evaluate(self, variables: dict[str, int]) -> int:
            return self.op(self.expr.evaluate(variables))

    ```

## Pratt parser

Notice that operators (`+`, `-`, etc.) and operands (`1`, `2`, etc.) appear as flat sequences in the parse tree. This is because we've not encoded any operator precedence into our grammar rules. This approach, along with the `PrattParser` helper class, is often the easiest to reason about and maintain.

!!! tip

    See `examples/calculator/grammar_encoded_prec.pest` and `examples/calculator/grammar_encoded_prec.py` for a complete example of encoding operator precedence in grammar rules and how it changes the way we process the parse tree.

    There's also `examples/calculator/prec_climber.py` that uses the same grammar as our Pratt parser but handles operator precedence without the use of the `PrattParser` helper class.

Using `pest.PrattParser` allows us to concisely declare operator precedence and infix operator associativity in an extensible way.

We've omitted some imports here for brevity. See `examples/calculator/pratt.py` for the complete code.

TODO: this example assumes a generated parser with `Rule` enum
TODO: rename to just `Calculator`

```python

class CalculatorParser(PrattParser[Expression]):
    """Example Pratt parser for a calculator grammar."""

    PREFIX_OPS: ClassVar[dict[str, int]] = {Rule.NEG: 6}

    POSTFIX_OPS: ClassVar[dict[str, int]] = {Rule.FAC: 7}

    INFIX_OPS: ClassVar[dict[str, tuple[int, bool]]] = {
        Rule.ADD: (3, PrattParser.LEFT_ASSOC),
        Rule.SUB: (3, PrattParser.LEFT_ASSOC),
        Rule.MUL: (4, PrattParser.LEFT_ASSOC),
        Rule.DIV: (4, PrattParser.LEFT_ASSOC),
        Rule.POW: (5, PrattParser.RIGHT_ASSOC),
    }

    def parse(self, program: str) -> Expression:
        pairs = parse(Rule.PROGRAM, program)
        return self.parse_expr(pairs.first().inner().first().stream())

    def parse_primary(self, pair: Pair) -> Expression:
        match pair:
            case Pair(Rule.INT):
                return IntExpr(int(pair.text))
            case Pair(Rule.IDENT):
                return VarExpr(pair.text)
            case Pair(Rule.EXPR):
                return self.parse_expr(pair.stream())
            case _:
                raise CalculatorSyntaxError(f"unexpected {pair.text!r}")

    def parse_prefix(self, op: Pair, rhs: Expression) -> Expression:
        if op.rule.name == Rule.NEG:
            return PrefixExpr(neg, rhs)
        raise CalculatorSyntaxError(f"unknown prefix operator {op.text!r}")

    def parse_postfix(self, lhs: Expression, op: Pair) -> Expression:
        if op.rule.name == Rule.FAC:
            return PostfixExpr(factorial, lhs)
        raise CalculatorSyntaxError(f"unknown postfix operator {op.text!r}")

    def parse_infix(self, lhs: Expression, op: Pair, rhs: Expression) -> Expression:
        match op.rule.name:
            case Rule.ADD:
                return InfixExpr(add, lhs, rhs)
            case Rule.SUB:
                return InfixExpr(sub, lhs, rhs)
            case Rule.MUL:
                return InfixExpr(mul, lhs, rhs)
            case Rule.DIV:
                return InfixExpr(floordiv, lhs, rhs)
            case Rule.POW:
                return InfixExpr(pow, lhs, rhs)
            case _:
                raise CalculatorSyntaxError(f"unknown infix operator {op.text!r}")
```
