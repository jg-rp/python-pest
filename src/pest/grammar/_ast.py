from typing import Literal

from ._tokens import Token

CHOICE: Literal[1] = 1
GROUP: Literal[2] = 2
OPTIONAL: Literal[3] = 3
REPEAT: Literal[4] = 4
REPEAT_ONCE: Literal[5] = 5
REPEAT_EXACT: Literal[6] = 6
REPEAT_MIN: Literal[7] = 7
REPEAT_MAX: Literal[8] = 8
REPEAT_MIN_MAX: Literal[9] = 9
POSITIVE_PREDICATE: Literal[10] = 10
NEGATIVE_PREDICATE: Literal[11] = 11
SEQUENCE: Literal[12] = 12
PUSH_LITERAL: Literal[13] = 13
PUSH: Literal[14] = 14
PEEK_SLICE: Literal[15] = 15
PEEK: Literal[16] = 16
PEEK_ALL: Literal[17] = 17
POP: Literal[18] = 18
POP_ALL: Literal[19] = 19
DROP: Literal[20] = 20
IDENT: Literal[21] = 21
STRING: Literal[22] = 22
CI_STRING: Literal[23] = 23
RANGE: Literal[24] = 24
RULE: Literal[25] = 25

type Expression = (
    Choice
    | Group
    | Optional
    | Repeat
    | RepeatOnce
    | RepeatExact
    | RepeatMin
    | RepeatMax
    | RepeatMinMax
    | PositivePredicate
    | NegativePredicate
    | Sequence
    | PushLiteral
    | Push
    | PeekSlice
    | Peek
    | PeekAll
    | Pop
    | PopAll
    | Drop
    | Ident
    | String
    | CIString
    | Range
    | Rule
)

type Choice = tuple[Literal[1], Token, tuple[Expression, ...]]  # | infix
type Group = tuple[Literal[2], Token, str | None, Expression]
type Optional = tuple[Literal[3], Token, Expression]  # ? postfix
type Repeat = tuple[Literal[4], Token, Expression]  # * postfix
type RepeatOnce = tuple[Literal[5], Token, Expression]  # + postfix
type RepeatExact = tuple[Literal[6], Token, Expression, int]  # {n} postfix
type RepeatMin = tuple[Literal[7], Token, Expression, int]  # {n,} postfix
type RepeatMax = tuple[Literal[8], Token, Expression, int]  # {,n} postfix
type RepeatMinMax = tuple[Literal[8], Token, Expression, int, int]  # {n,m} postfix
type PositivePredicate = tuple[Literal[10], Token, str | None, Expression]  # & prefix
type NegativePredicate = tuple[Literal[11], Token, str | None, Expression]  # ! prefix
type Sequence = tuple[Literal[12], Token, tuple[Expression, ...]]  # ~ infix

type PushLiteral = tuple[Literal[13], Token, str | None, str]
type Push = tuple[Literal[14], Token, str | None, Expression]
type PeekSlice = tuple[Literal[15], Token, str | None, int | None, int | None]
type Peek = tuple[Literal[16], Token]
type PeekAll = tuple[Literal[17], Token]
type Pop = tuple[Literal[18], Token]
type PopAll = tuple[Literal[19], Token]
type Drop = tuple[Literal[20], Token]
type Ident = tuple[Literal[21], Token, str | None, str]  # Name of a rule
type String = tuple[Literal[22], Token, str]
type CIString = tuple[Literal[23], Token, str]  # Case insensitive string
type Range = tuple[Literal[24], Token, str | None, str, str]

# (type, token, name, expression, modifier, doc)
type Rule = tuple[Literal[25], Token, str, Expression, int, tuple[str]]
