# Parsing with Python Pest

Python Pest is a port of the [Rust Pest](https://pest.rs/) parsing library - a powerful, elegant PEG (Parsing Expression Grammar) parser generator.

It brings the same expressive grammar syntax and predictable parsing model to Python, while preserving Pest's clean and declarative approach to grammar design.

Python Pest uses exactly the same grammar syntax as Pest v2, so existing Pest grammars can be used without modification.

It also provides a token pair API that closely mirrors Rust Pest's `Pair` and `Pairs` interfaces, making it immediately familiar to anyone who has used Pest in Rust.

If you're new to Pest or PEG parsers, we highly recommend reading through the [Pest Book](https://pest.rs/book/). Even if you're not a Rust developer, the book provides an excellent introduction to the core ideas behind Pest's grammar syntax, parsing model, and design philosophy - all of which apply directly to Python Pest.

Python Pest aims to feel native in Python while staying true to the spirit and strengths of the original Rust Pest library.

## Conceptual overview

When writing a hand-crafted parser, we typically start with a lexer (also called a scanner or tokenizer). The lexer scans raw input text and produces a stream of tokens - symbolic representations of meaningful units like identifiers, keywords, or punctuation.

A parser then consumes those tokens according to the language's grammar and constructs an abstract syntax tree (AST) or another intermediate structure.

```
Lexer -> Tokens -> Parser -> AST ..
```

This approach gives you fine-grained control over every stage, but it also means you have to define both the tokenization and parsing logic by hand - including the rules, ordering, and tree construction.

When using Pest, we instead start by writing a grammar using Pest's expressive PEG (Parsing Expression Grammar) syntax. Pest uses this grammar to automatically generate a parse tree from input text.

Each non-silent rule in the grammar appears as a node in the parse tree, paired with its matched text. You can then traverse this tree to build your own AST or evaluate results directly.

```
Grammar -> Parse Tree -> Parser -> AST ..
```

Compared to a hand-crafted parser, Pest's parse trees are more structurally rich. They mirror the hierarchy of your grammar rather than producing a flat stream of tokens. This makes it easier to reason about nesting, precedence, and composition.

In short:

- Hand-crafted parsers require explicit control over lexing and parsing.
- Pest parsers let you define the grammar declaratively and focus on transforming the resulting structured tree into meaningful data.

## Parse trees and token pairs

When you parse input with Python Pest, the result is a parse tree - a hierarchical representation of how your input text matched the grammar. Each node in this tree corresponds to a grammar rule that successfully matched part of the input.

At the core of this structure is the `Pair` class. A `Pair` represents a pair of tokens: the start and end markers that delimit a substring of the original input. In other words, every `Pair` knows:

- which rule it matched (`pair.name` or `pair.rule.name`),
- the span of input text it covers (`pair.text` or `str(pair)`),
- and any nested rules it contains (`for child in pair:` or `pair.inner()`).

This structure mirrors your grammar exactly. If a rule in your grammar contains other rules, those inner rules appear as child `Pair` objects within the parent. Together, these pairs form the parse tree, which captures both the structure and meaning of your input.

For example, using the calculator grammar in `examples/calculator/grammar_encoded_prec.pest`, the input `2 * 3 + 4` produces a parse tree like this:

```
- program
  - expr > add_sub
    - mul_div
      - pow_expr > prefix > postfix > int: "2"
      - mul: "*"
      - pow_expr > prefix > postfix > int: "3"
    - add: "+"
    - mul_div > pow_expr > prefix > postfix > int: "4"
  - EOI: ""
```

Notice that `2 * 3` is nested deeper than `+ 4`, encoding the fact that multiplication has higher precedence that addition.

In practice, you'll typically walk the parse tree to transform it into a more useful data structure, such as an abstract syntax tree (AST) or a Python object model.

### Destructuring token pairs

Python Pest’s Pair class defines [`__match_args__`](https://peps.python.org/pep-0636/#matching-positional-attributes):

```python
__match_args__ = ("name", "children")
```

This makes `Pair` objects integrate seamlessly with Python's [structural pattern matching](https://peps.python.org/pep-0636/) (`match`/`case`). You can destructure pairs directly by their rule name and child structure, making parse tree traversal both concise and expressive. This example comes from `examples/jsonpath/jsonpath.py`.

```python
def parse_segment(self, segment: Pair) -> Segment:
    match segment:
        case Pair(Rule.CHILD_SEGMENT, [inner]):
            return ChildSegment(segment, self.parse_segment_inner(inner))
        case Pair(Rule.DESCENDANT_SEGMENT, [inner]):
            return RecursiveDescentSegment(segment, self.parse_segment_inner(inner))
        case Pair(Rule.NAME_SEGMENT, [inner]) | Pair(Rule.INDEX_SEGMENT, [inner]):
            return ChildSegment(segment, [self.parse_selector(inner)])
        case _:
            raise JSONPathSyntaxError("expected a segment", segment)
```

## Grammar syntax quick reference

For a complete explanation of grammar syntax see the official [Pest Book](https://pest.rs/book/grammars/syntax.html).

### Grammar rule

```{title="syntax"}
rule = { ... }
```

Defines a standard grammar rule. Rules can refer to other rules by name.

```{title="example"}
ident = { ASCII_ALPHA+ }
```

`ASCII_ALPHA` is a built-in rule. See the Pest book for a complete list of [built-in rules](https://pest.rs/book/grammars/built-ins.html).

### Silent rule

```{title="syntax"}
rule = _{ ... }
```

A silent rule matches input but does not appear in the parse tree. `WHITESPACE` is a special rule. If defined, it enables implicit whitespace between items in a [sequence](#sequence) and when [repeating](#repetition) expressions.

```{title="example"}
WHITESPACE = _{ " " }
```

### Atomic rule

```{title="syntax"}
rule = _{ ... }
```

An atomic rule disables implicit whitespace and hides all inner rules, producing a single leaf node in the parse tree.

```{title="example"}
int = @{ ASCII_DIGIT+ }
```

### Compound atomic rule

```{title="syntax"}
rule = ${ ... }
```

A compound atomic rule disables implicit whitespace but keeps inner rules visible in the parse tree.

```{title="example"}
full_time = ${ partial_time ~ time_offset }
```

### Non-atomic rule

```{title="syntax"}
rule = !{ ... }
```

Cancels atomicity if called from an atomic parent rule.

```{title="example"}
expr = !{ term ~ ("+" ~ term)* }
```

### String literal

```{title="syntax"}
"..."
```

Matches an exact string, case-sensitively. String literals can contain escape sequences including Unicode escapes.

```{title="example"}
"let"
```

### Case-insensitive string

```{title="syntax"}
^"..."
```

Matches a string, case-insensitively.

```{title="example"}
^"select"
```

### Character range

```{title="syntax"}
'a'..'z'
```

Matches any character within the specified inclusive range. Unicode escapes are supported.

```{title="example"}
'\u{80}'..'\u{D7FF}'
```

### Any character

```{title="syntax"}
ANY
```

Matches any single character.

### Sequence

```{title="syntax"}
A ~ B
```

Matches A followed by B, with implicit whitespace between them if the special `WHITESPACE` rule is defined, unless inside an atomic context.

```{title="example"}
"[" ~ int_list ~ "]"
```

### Ordered choice

```{title="syntax"}
A | B
```

Matches A or B, choosing the first successful alternative. PEG grammars are deterministic - once a branch succeeds, the others are not tried.

```{title="example"}
"a" | "b"
```

### Grouping

```{title="syntax"}
( ... )
```

Groups expressions and controls operator precedence.

```{title="example"}
( A | B )*
```

### Repetition

```{title="syntax"}
*
+
?
{n}
{m,n}
```

Control how many times a pattern repeats:

- `*` - zero or more
- `+` - one or more
- `?` - optional (zero or one)
- `{n}` - exactly n times
- `{m,n}` - between m and n times (inclusive). Either `m` or `n` can be omitted.

```{title="examples"}
ASCII_DIGIT*
ASCII_DIGIT+
"-"?
ASCII_HEX_DIGIT{2}
hex_digit{2, 6}
```

### Positive predicate

```{title="syntax"}
&A
```

Positive lookahead succeeds if `A` matches but does not consume input.

```{title="example"}
ident ~ &"="
```

### Negative predicate

```{title="syntax"}
!A
```

Negative lookahead succeeds if `A` **does not** match.

```{title="example"}
literal ~ !"="
```

### Stack operations

```{title="syntax"}
PUSH(expr)
PUSH_LITERAL("...")
POP
PEEK
PEEK[..]
DROP
PEEK_ALL
```

Pest provides a stack for stateful parsing.

- `PUSH(expr)` - Match `expr` and push the matched string onto the stack
- `PUSH_LITERAL("...")` - Push a string literal onto the stack. Never fails.
- `POP` - Remove and match the value at the top of the stack.
- `PEEK` - Match the value on the top oof the stack without removing it.
- `PEEK` - Match a slice of the stack from bottom to top.
- `DROP` - Pop from the stack without matching. Fails if the stack is empty.
- `PEEK_ALL` - Match all items from the stack from top to bottom.

```{title="examples"}
PUSH(A)
PUSS("a")
POP
PEEK
PEEK[1..3]
DROP
PEEK_ALL
```

### Tags

```{title="syntax"}
#tag=A
```

Tags label expressions for later reference or tooling. Tags are always enabled in Python Pest.

```{title="example"}
#literal = hex_digit{2, 6}
```
