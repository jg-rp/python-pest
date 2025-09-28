# Python Pest Grammar AST with Code Generation

## Grammar Internal Representation

```
- Expression
  - Rule
    - GrammarRule (user defined rules)
    - BuiltInRule
      - Any
      - ASCIIRule
      - EOI
      - SOI
      - UnicodePropertyRule
  - Terminal
    - CaseInsensitiveString
    - CharacterRange
    - Drop
    - Peek
    - PeekAll
    - PeekSlice
    - Pop
    - PopAll
    - PushLiteral
    - String
  - Choice
  - Group
  - Identifier
  - NegativePredicate
  - Optional
  - PositivePredicate
  - Push
  - Repeat
  - RepeatExact
  - RepeatMax
  - RepeatMin
  - RepeatMinMax
  - RepeatOnce
  - Sequence
  - SkipUntil (optimized neg pred any)
```

## `Expression.generate()`

`def generate(self, gen: Builder, state_var: str, pairs_var: str) -> None: ...`

- `gen` is our code generation helper to which we write Python code. There is exactly one `Builder` per generated rule function. It gets passed around to every sub expression in the grammar AST.
- `state_var` is the name of the variable holding the current parser state. (We could hard code this as `state`. There's only ever going to be one state object per generated rule function.)
- `pairs_var` is the name of the variable holding a list of `Pair` instances. Some expressions will need intermediate pair lists before deciding whether to append them to the rule's pairs list.

## Generated Functions

We call `generate_rule` on every `Rule` instance to bootstrap rule code generation.

```python
def generate_rule(rule: Rule) -> str:
    gen = Builder()
    # `Rule.generate` ignores `state_var` and `pairs_var`.
    # `state_var` is always "state" for rules
    # `pairs_var` is always "pairs" for rules
    rule.generate(gen, "", "")
    return gen.render()
```

The returned string is a single function `def parse_<rule name>(state: ParserState) -> Pairs:`.

`Rule.generate` is responsible for respecting the rule's modifier, wrapping or silencing child pairs as necessary.

## Example

Given the simple grammar `thing = { "a" ~ "b" }`:

```python
rules = Parser.from_grammar('thing = { "a" ~ "b" }').rules
print(generate_rule(rules["thing"]))
```

We get the following generated function.

```python
def parse_thing(state) -> Pairs:
    pairs = []
    if state.input.startswith('a', state.pos):
        state.pos += 1
    else:
        raise ParseError('a')
    if state.input.startswith('b', state.pos):
        state.pos += 1
    else:
        raise ParseError('b')
    return Pairs(pairs)
```
