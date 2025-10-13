"""Transform Rep-NegPred-Any into a SkipUntil expression.

Example Input:

```
Repeat                                '(!("a" | "b") ~ ANY)*'
    └── Group                         '(!("a" | "b") ~ ANY)'
        └── Sequence                  '!("a" | "b") ~ ANY'
            ├── NegativePredicate     '!("a" | "b")'
            │   └── Group             '("a" | "b")'
            │       └── Choice        '"a" | "b"'
            │           ├── String    '"a"'
            │           └── String    '"b"'
            └── Any                   'ANY'
                └── _Any              'ANY'
```

After a "skip" pass we get a single, optimized `SkipUntil` expression.

```
SkipUntil                             '(!("a" | "b") ~ ANY)*'
```
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pest.grammar import Choice
from pest.grammar import Group
from pest.grammar import Identifier
from pest.grammar import NegativePredicate
from pest.grammar import Repeat
from pest.grammar import Rule
from pest.grammar import Sequence
from pest.grammar import SkipUntil
from pest.grammar import String
from pest.grammar.rules.special import Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pest.grammar import Expression


def skip(expr: Expression, rules: Mapping[str, Rule]) -> Expression:
    """Transform Rep-NegPred-Any into a SkipUntil expression."""
    # NOTE: The reference implementation only applies "skip" to atomic type rules.
    # As far as I can tell, this is acting like an "early return" as the "ANY" in
    # Rep-NegPred-Any would consume whitespace and comments.
    match expr:
        case Repeat(expression=Group(expression=Sequence(expressions=[left, right]))):
            match (left, right):
                case (NegativePredicate(expression=inner), Any()) if isinstance(
                    inner, Rule
                ):
                    new_expr = _skip(inner.expression, rules, [])
                    if new_expr:
                        return new_expr
                case (NegativePredicate(expression=inner), Any() | Identifier("ANY")):
                    new_expr = _skip(inner, rules, [])
                    if new_expr:
                        return new_expr
                case _:
                    return expr
        case _:
            return expr

    return expr


def _skip(
    expr: Expression, rules: Mapping[str, Rule], subs: list[str]
) -> SkipUntil | None:
    if isinstance(expr, Group):
        expr = expr.expression

    if isinstance(expr, Choice):
        for ex in expr.expressions:
            inlined_subs = _skip(ex, rules, subs)
            if not inlined_subs:
                return None
        return SkipUntil(subs)

    if isinstance(expr, SkipUntil):
        subs.extend(expr.subs)
        return SkipUntil(subs)

    if isinstance(expr, String):
        subs.append(expr.value)
        return SkipUntil(subs)

    if isinstance(expr, Identifier):
        rule = rules.get(expr.value)
        if rule:
            return _skip(rule.expression, rules, subs)

    return None
