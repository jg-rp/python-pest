"""Transform Rep{Once,Exact,Min,Max,MinMax} to Seq.

Example input:

```
RepeatExact           'a{3}'
    └── Identifier    'a'
```

After an "unroll" pass we get a sequence.

```
Sequence              'a ~ a ~ a'
    ├── Identifier    'a'
    ├── Identifier    'a'
    └── Identifier    'a'
```
"""

from __future__ import annotations

from itertools import chain
from itertools import repeat
from typing import TYPE_CHECKING

from pest.grammar import Group
from pest.grammar import Optional
from pest.grammar import Repeat
from pest.grammar import RepeatExact
from pest.grammar import RepeatMax
from pest.grammar import RepeatMin
from pest.grammar import RepeatMinMax
from pest.grammar import RepeatOnce
from pest.grammar import Rule
from pest.grammar import Sequence

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pest.grammar import Expression


def unroll(expr: Expression, _rules: Mapping[str, Rule]) -> Expression:  # noqa: PLR0911
    """Transform Rep{Once,Exact,Min,Max,MinMax} to Seq."""
    match expr:
        case RepeatOnce(expression=inner):
            if isinstance(inner, Group):
                return Sequence(inner.expression, Repeat(inner))
            return Sequence(inner, Repeat(inner))
        case RepeatExact(expression=inner, number=num):
            return Sequence(*repeat(inner, num))
        case RepeatMin(expression=inner, number=num):
            return Sequence(*chain(repeat(inner, num), [Repeat(inner)]))
        case RepeatMax(expression=inner, number=num):
            return Sequence(*repeat(Optional(inner), num))
        case RepeatMinMax(expression=inner, min=min_, max=max_):
            return Sequence(
                *chain(repeat(inner, min_), repeat(Optional(inner), max_ - min_))
            )
        case _:
            return expr
