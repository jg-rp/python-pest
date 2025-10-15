# Python Pest

Python Pest is a port of the [Rust Pest](https://pest.rs/) parsing library - a powerful, elegant PEG (Parsing Expression Grammar) parser generator. We use exactly the same grammar syntax as Pest v2, so existing Pest grammars can be used without modification.

## Install

Use `pip` or your favorite package manager.

```
python -m pip install python-pest
```

## Example

Let's say we want to parse input like:

```json
[1, 2, 3, 42]
```

Our grammar is just a Python string, possibly read from a file (reading from a file means we don't need to worry about double escaping):

```
array      = { "[" ~ int_list ~ "]" }
int_list   = { int ~ ("," ~ int)* }
int        = @{ "0" | ASCII_NONZERO_DIGIT  ~ ASCII_DIGIT* }
WHITESPACE = _{ " " }
```

`array`, `int_list`, `int` and `WHITESPACE` are [rules](overview.md#grammar-rule). A rule can reference other rules by name. `~` means [followed by](overview.md#sequence) and `|` is [ordered choice](overview.md#ordered-choice).

To use a Pest grammar in Python we pass it to the static method `Parser.from_grammar()`, which returns a new instance of `Parser`.

```python
from pest import Pair
from pest import Parser

# Read grammar rules from a file.
with open("example.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)
```

Instances of `Parser` have a `parse()` method that takes the name of the rule to start parsing from and the input text to parse. Here we parse our example input and dump a compact representation of the resulting parse tree.

```python
# ... continued
parse_tree = parser.parse("array", "[1, 2, 3, 42]")

print(parse_tree.dumps())
# - array > int_list
#   - int: "1"
#   - int: "2"
#   - int: "3"
#   - int: "42"
```

??? tip "Debug output"

    A more detailed parse tree representation is available by passing `compact=False` to `Pairs.dumps()`.

    ```python
    print(parse_tree.dumps(compact=False))
    ```

    ```json
    [
      {
        "rule": "array",
        "span": {
          "str": "[1, 2, 3, 42]",
          "start": 0,
          "end": 13
        },
        "inner": [
          {
            "rule": "int_list",
            "span": {
              "str": "1, 2, 3, 42",
              "start": 1,
              "end": 12
            },
            "inner": [
              {
                "rule": "int",
                "span": {
                  "str": "1",
                  "start": 1,
                  "end": 2
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
              },
              {
                "rule": "int",
                "span": {
                  "str": "3",
                  "start": 7,
                  "end": 8
                },
                "inner": []
              },
              {
                "rule": "int",
                "span": {
                  "str": "42",
                  "start": 10,
                  "end": 12
                },
                "inner": []
              }
            ]
          }
        ]
      }
    ]
    ```

A parse tree is composed of token `Pair` and `Pairs` types, where each node represents a matched grammar rule and all descendant rules. To make traversing and transforming that tree expressive and type-safe, we recommend using Python's [structural pattern matching](https://peps.python.org/pep-0636/) (`match`/`case`) syntax. It lets you destructure parse tree nodes directly by rule name and inner content, clearly showing what each branch of your parser expects.

For this very simple example, we need just one match expression to match the `array` token pair and unpack its inner `int_list`.

```python
# ... continued
match parse_tree.first():
    case Pair("array", [Pair("int_list", inner)]):
        numbers = [int(p.text) for p in inner]
    case _:
        raise ValueError("unexpected parse tree")

print(numbers)
```

### Code generation

So far we've parsed input text directly from a grammar tree (the `Parser` instance), but you can also generate a Python module with `Parser.generate()`. This is something you'd do once after modifying your grammar.

TODO: Show how to do this with the CLI - once I've written it.

```python
# ... continued
with open("parser.py", "w", encoding="utf-8") as fd:
    fd.write(parser.generate())
```

Generated parser modules expose a `parse()` function, a `Rule` enum and a simple command line interface for testing your generated parser manually.

!!! important

    This example is not continued from above. We are importing from the `parser.py` module we've just generated.

```python
from parser import Rule
from parser import parse
from pest import Pair

parse_tree = parse(Rule.ARRAY, "[1, 2, 3, 42]")

match parse_tree.first():
    case Pair(Rule.ARRAY, [Pair(Rule.INT_LIST, inner)]):
        numbers = [int(p.text) for p in inner]
    case _:
        raise ValueError("unexpected parse tree")

print(numbers)
```

Parse trees obtained from generated code are identical to those returned by `Parser.parse()`.

## More examples

More involved and realistic examples can be found in the `examples/` folder in the root of this projects source tree.

`examples/jsonpath` is an implementation of RFC 9535 that uses the precedence climbing technique to handle operator precedence. You can compare it directly to [python-jsonpath-rfc9535](https://github.com/jg-rp/python-jsonpath-rfc9535), which is implemented with a hand-crafted parser and identical internal representation.

`examples/calculator` shows three different approaches to handling operator precedence:

- `examples/calculator/prec_climber.py` - [Precedence climbing method](https://en.wikipedia.org/wiki/Operator-precedence_parser#Precedence_climbing_method),
- `examples/calculator/pratt.py` - [Pratt parsing](https://en.wikipedia.org/wiki/Operator-precedence_parser#Pratt_parsing) (this one is the most readable),
- `examples/calculator/grammar_encoded_prec.py` - precedence encoded directly in the grammar.
