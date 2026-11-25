from __future__ import annotations

import copy
import json
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generator

from .grammar import _ast as ast
from .grammar._modifiers import ATOMIC, COMPOUND, NONATOMIC, SILENT
from .grammar._parser import Parser as Grammar
from .pairs import Pair, Pairs

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .grammar._ast import Expression, Rule


class Parser:
    __slots__ = ("doc", "rules")

    def __init__(self, rules: dict[str, Rule], doc: list[str]):
        self.rules = rules
        self.doc = doc

    @classmethod
    def from_grammar(cls, grammar: str) -> Parser:
        rules, doc = Grammar.parse(grammar)
        return cls(rules, doc)

    def parse(self, start_rule: str, text: str, *, start_pos: int = 0) -> Pairs:
        pairs: list[Pair] = []
        _Parse(self.rules, text, start_pos).parse_rule(self.rules[start_rule], pairs)
        return Pairs(pairs)


class _Parse:
    __slots__ = (
        "_trivia",
        "_suppress_failures",
        "furthest_expected",
        "furthest_pos",
        "furthest_stack",
        "furthest_unexpected",
        "history",
        "neg_pred_depth",
        "rules",
        "source",
        "state",
        "tags",
    )

    def __init__(self, rules: dict[str, Rule], text: str, start_pos: int) -> None:
        self.rules = rules
        self.source = text

        self.state = _ParseState(pos=start_pos)
        self.history: list[_ParseState] = []

        self.tags: list[str] = []

        self._trivia = "WHITESPACE" in rules or "COMMENT" in rules
        self._suppress_failures = False
        self.neg_pred_depth = 0

        # Failure tracking
        self.furthest_pos = -1
        self.furthest_expected: dict[str, list[str]] = {}
        self.furthest_unexpected: dict[str, list[str]] = {}
        self.furthest_stack: list[Rule] = []

    def checkpoint(self) -> None:
        self.history.append(copy.deepcopy(self.state))

    def ok(self) -> None:
        self.history.pop()

    def restore(self) -> None:
        self.state = self.history.pop()

    def push(self, value: str) -> None:
        self.state.stack.append(value)

    def drop(self) -> None:
        self.state.stack.pop()

    def peek(self) -> str | None:
        self.state.stack[-1] if self.state.stack else None

    def peek_slice(
        self, start: int | None = None, end: int | None = None
    ) -> Sequence[str]:
        if start is None and end is None:
            return self.state.stack[:]
        return self.state.stack[slice(start, end)]

    @contextmanager
    def atomic_checkpoint(self, rule: Rule) -> Generator[_Parse, None, None]:
        depth = self.state.atomic_depth
        self.state.rules.append(rule)
        yield self
        self.state.rules.pop()
        self.state.atomic_depth = depth

    @contextmanager
    def rule(self, rule: Rule) -> Generator[_Parse, None, None]:
        self.state.rules.append(rule)
        yield self
        self.state.rules.pop()

    @contextmanager
    def suppress_failures(self) -> Generator[_Parse, None, None]:
        self._suppress_failures = True
        yield self
        self._suppress_failures = False

    @contextmanager
    def tag(self, tag_: str) -> Generator[_Parse, None, None]:
        self.tags.append(tag_)
        yield self
        if self.tags:
            self.tags.pop()

    def fail(
        self,
        label: str,
        *,
        pos: int | None = None,
        rule_name: str | None = None,
        force: bool = False,
    ) -> None:
        """Record a failure, inferring expected vs. unexpected context."""
        if (self.neg_pred_depth > 0 and not force) or self._suppress_failures:
            return

        is_neg_context = self.neg_pred_depth % 2 == 1
        rule_name = rule_name or self.state.rules[-1][2]
        pos = pos or self.state.pos

        if pos > self.furthest_pos:
            self.furthest_pos = pos
            self.furthest_stack = list(self.state.rules)
            if is_neg_context:
                self.furthest_unexpected = {rule_name: [label]}
                self.furthest_expected = {}
            else:
                self.furthest_expected = {rule_name: [label]}
                self.furthest_unexpected = {}
        elif pos == self.furthest_pos:
            target = (
                self.furthest_unexpected if is_neg_context else self.furthest_expected
            )

            if rule_name in target:
                target[rule_name].append(label)
            else:
                target[rule_name] = [label]

    def parse_rule(self, rule: Rule, pairs: list[Pair]) -> bool:
        start = self.state.pos
        children: list[Pair] = []

        _, _, name, expression, modifier, _ = rule

        if modifier & (ATOMIC | COMPOUND) or name in (
            "COMMENT",
            "WHITESPACE",
        ):
            with self.atomic_checkpoint(rule):
                self.state.atomic_depth += 1
                matched = self.parse_expression(expression, children)

        elif modifier & NONATOMIC:
            with self.atomic_checkpoint(rule):
                self.state.atomic_depth = 0
                matched = self.parse_expression(expression, children)

        else:
            with self.rule(rule):
                matched = self.parse_expression(expression, children)

        if not matched:
            return False

        if modifier & SILENT:
            # Children without an enclosing Pair.
            pairs.extend(children)
            return True

        if modifier & ATOMIC:
            effective_rule: Rule | None

            match expression:
                case (ast.RULE, _, _, _, _, _):
                    effective_rule = expression
                case (ast.IDENT, _, _, rule_name):
                    effective_rule = self.rules.get(rule_name)
                case _:
                    effective_rule = None

            if not effective_rule or not effective_rule[4] & (NONATOMIC | COMPOUND):
                # Atomic rule silences children
                children = []

        pairs.append(
            Pair(
                input_=self.source,
                rule=rule,
                start=start,
                end=self.state.pos,
                children=children,
                tag=self.tags.pop() if self.tags else None,
            )
        )

        return True

    def parse_expression(self, expression: Expression, pairs: list[Pair]) -> bool:
        match expression:
            case (ast.IDENT, _, tag, name):
                rule = self.rules[name]

                if tag:
                    with self.tag(tag):
                        return self.parse_rule(rule, pairs)

                return self.parse_rule(rule, pairs)

            case (ast.RULE, _, _, _, _, _):
                return self.parse_rule(expression, pairs)

            case (ast.CHOICE, _, left, right):
                self.checkpoint()
                children: list[Pair] = []

                if self.parse_expression(left, children):
                    self.ok()
                    pairs.extend(children)
                    return True

                self.restore()
                self.checkpoint()

                if self.parse_expression(right, children):
                    self.ok()
                    pairs.extend(children)
                    return True

                self.restore()
                return False

            case (ast.SEQUENCE, _, left, right):
                children: list[Pair] = []

                if not self.parse_expression(left, children):
                    return False

                self.parse_trivia(children)

                if not self.parse_expression(right, children):
                    return False

                pairs.extend(children)
                return True

            case (ast.GROUP, _, tag, expr):
                if tag:
                    with self.tag(tag):
                        return self.parse_expression(expr, pairs)
                return self.parse_expression(expr, pairs)

            case (ast.POSITIVE_PREDICATE, _, tag, expr):
                self.checkpoint()
                matched = self.parse_expression(expr, [])
                self.restore()
                return matched

            case (ast.NEGATIVE_PREDICATE, _, tag, expr):
                self.checkpoint()
                self.neg_pred_depth += 1
                matched = self.parse_expression(expr, [])
                self.restore()

                if matched:
                    # If expr is a rule, by now it has been popped off the stack.
                    match expr:
                        case (ast.RULE, _, rule_name, ex, _, _):
                            self.fail(
                                serialize_expression(ex),
                                rule_name=rule_name,
                                force=True,
                            )
                        case (ast.IDENT, _, _, rule_name):
                            self.fail(
                                serialize_expression(self.rules[rule_name][3]),
                                rule_name=rule_name,
                                force=True,
                            )
                        case _:
                            self.fail(serialize_expression(expr), force=True)

                self.neg_pred_depth -= 1
                return not matched

            case (ast.OPTIONAL, _, expr):
                self.checkpoint()
                children: list[Pair] = []

                if self.parse_expression(expr, children):
                    self.ok()
                    pairs.extend(children)
                    return True

                self.restore()
                return True

            case (ast.REPEAT, _, expr):
                children: list[Pair] = []

                while True:
                    self.checkpoint()

                    if not self.parse_expression(expr, children):
                        self.restore()
                        break

                    self.ok()
                    self.parse_trivia(children)
                    pairs.extend(children)
                    children.clear()

                return True

            case (ast.REPEAT_ONCE, _, expr):
                children: list[Pair] = []

                self.checkpoint()

                if not self.parse_expression(expr, children):
                    self.restore()
                    return False

                self.ok()
                pairs.extend(children)
                children.clear()

                while True:
                    self.checkpoint()

                    if not self.parse_expression(expr, children):
                        self.restore()
                        break

                    self.ok()
                    self.parse_trivia(children)
                    pairs.extend(children)
                    children.clear()

                return True

            case (ast.REPEAT_EXACT, _, expr, n):
                if n <= 0:
                    return True

                accumulator: list[Pair] = []
                children: list[Pair] = []
                match_count = 0

                self.checkpoint()

                while True:
                    self.checkpoint()

                    if not self.parse_expression(expr, children):
                        self.restore()
                        break

                    self.ok()
                    self.parse_trivia(children)
                    accumulator.extend(children)
                    children.clear()
                    match_count += 1

                    if match_count >= n:
                        break

                if match_count == n:
                    pairs.extend(accumulator)
                    self.ok()
                    return True

                self.restore()
                return False

            case (ast.REPEAT_MIN, _, expr, n):
                accumulator: list[Pair] = []
                children: list[Pair] = []
                match_count = 0

                self.checkpoint()

                while True:
                    self.checkpoint()

                    if not self.parse_expression(expr, children):
                        self.restore()
                        break

                    self.ok()
                    self.parse_trivia(children)
                    accumulator.extend(children)
                    children.clear()
                    match_count += 1

                if match_count >= n:
                    pairs.extend(accumulator)
                    self.ok()
                    return True

                self.restore()
                return False

            case (ast.REPEAT_MAX, _, expr, n):
                if n <= 0:
                    return True

                accumulator: list[Pair] = []
                children: list[Pair] = []
                match_count = 0

                self.checkpoint()

                while True:
                    self.checkpoint()

                    if not self.parse_expression(expr, children):
                        self.restore()
                        break

                    self.ok()
                    self.parse_trivia(children)
                    accumulator.extend(children)
                    children.clear()
                    match_count += 1

                    if match_count >= n:
                        break

                if match_count <= n:
                    pairs.extend(accumulator)
                    self.ok()
                    return True

                self.restore()
                return False

            case (ast.REPEAT_MIN_MAX, _, expr, min_, max_):
                accumulator: list[Pair] = []
                children: list[Pair] = []
                match_count = 0

                self.checkpoint()

                while True:
                    self.checkpoint()

                    if not self.parse_expression(expr, children):
                        self.restore()
                        break

                    self.ok()
                    self.parse_trivia(children)
                    accumulator.extend(children)
                    children.clear()
                    match_count += 1

                    if match_count >= max_:
                        break

                if min_ <= match_count <= max_:
                    pairs.extend(accumulator)
                    self.ok()
                    return True

                self.restore()
                return False

            case (ast.PUSH_LITERAL, _, _, value):
                self.push(value)
                return True

            case (ast.PUSH, _, _, expr):
                start = self.state.pos
                children: list[Pair] = []

                if not self.parse_expression(expr, children):
                    return False

                self.push(self.source[start : self.state.pos])
                pairs.extend(children)
                return True

            case (ast.PEEK_SLICE, _, _, start, stop):
                pos = self.state.pos

                for literal in self.peek_slice(start, stop):
                    if self.source.startswith(literal, pos):
                        pos += len(literal)
                        # TODO: parse_trivia?
                    else:
                        self.fail(literal)
                        return False

                self.state.pos = pos
                return True

            case (ast.PEEK, _, _):
                value = self.peek()

                if value is not None and self.source.startswith(value, self.state.pos):
                    self.state.pos += len(value)
                    return True

                if value:
                    self.fail(value)

                return False

            case (ast.PEEK_ALL, _, _):
                pos = self.state.pos
                length = len(self.state.stack)
                children: list[Pair] = []

                for i, literal in enumerate(self.state.stack):
                    if not self.source.startswith(literal, pos):
                        self.fail(literal)
                        return False

                    pos += len(literal)

                    if i < length - 1:
                        self.parse_trivia(children)

                self.state.pos = pos
                pairs.extend(children)
                return True

            case (ast.POP, _, _):
                value = self.peek()

                if value is not None and self.source.startswith(value, self.state.pos):
                    self.state.stack.pop()
                    self.state.pos += len(value)
                    return True

                if value:
                    self.fail(value)

                return False

            case (ast.POP_ALL, _, _):
                pos = self.state.pos
                children: list[Pair] = []
                length = len(self.state.stack)

                self.checkpoint()

                for i, literal in enumerate(reversed(self.state.stack)):
                    if not self.source.startswith(literal, pos):
                        self.restore()
                        self.fail(literal)
                        return False

                    pos += len(literal)

                    if i < length - 1:
                        self.parse_trivia(children)

                self.state.stack.clear()
                self.ok()
                self.state.pos = pos
                pairs.extend(children)
                return True

            case (ast.DROP, _, _):
                if self.state.stack:
                    self.state.stack.pop()
                    return True

                self.fail("drop from empty stack")
                return False

            case (ast.STRING, _, value):
                if self.source.startswith(value, self.state.pos):
                    self.state.pos += len(value)
                    return True

                self.fail(json.dumps(value))
                return False

            case (ast.CI_STRING, _, value):
                if self.source[self.state.pos : len(value)].lower() == value.lower():
                    self.state.pos += len(value)
                    return True

                self.fail(json.dumps(value))
                return False

            case (ast.RANGE, _, _, start, stop):
                ch = ord(self.source[self.state.pos])

                if ch >= ord(start) and ch <= ord(stop):
                    self.state.pos += 1
                    return True

                self.fail(f"{start!r}..{stop!r}")
                return False

    def parse_trivia(self, pairs: list[Pair]) -> bool:
        if not self._trivia or self.state.atomic_depth > 0:
            return False

        whitespace_rule = self.rules.get("WHITESPACE")
        comment_rule = self.rules.get("COMMENT")

        children: list[Pair] = []
        matched = False

        with self.suppress_failures():
            while True:
                found = False

                if whitespace_rule:
                    if self.parse_rule(whitespace_rule, children):
                        matched = found = True
                        pairs.extend(children)

                    children.clear()

                if comment_rule:
                    self.checkpoint()

                    if self.parse_rule(comment_rule, children):
                        matched = found = True
                        pairs.extend(children)
                        self.ok()
                    else:
                        self.restore()

                    children.clear()

                if not found:
                    break

        return matched


@dataclass(slots=True)
class _ParseState:
    pos: int
    atomic_depth: int = 0
    rules: list[Rule] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    stack: list[str] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]


def serialize_expression(expr: Expression) -> str:
    # TODO:
    raise NotImplementedError
