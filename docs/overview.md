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

TODO:

## More examples

TODO:
