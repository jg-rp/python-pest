from __future__ import annotations

from typing import TYPE_CHECKING

import regex as re

from pest.grammar.codegen.state import ParseError
from pest.grammar.codegen.state import RuleFrame
from pest.grammar.codegen.state import State
from pest.grammar.rule import ATOMIC
from pest.grammar.rule import COMPOUND
from pest.grammar.rule import NONATOMIC
from pest.grammar.rule import SILENT
from pest.grammar.rule import SILENT_ATOMIC
from pest.grammar.rule import SILENT_COMPOUND
from pest.grammar.rule import SILENT_NONATOMIC
from pest.pairs import Pair
from pest.pairs import Pairs

if TYPE_CHECKING:
    from collections.abc import Callable

# ruff: noqa: D103 N802 N816 N806 PLR0912 PLR0915


def _parse_http() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("http", 0)

    def inner(state: State) -> Pairs:
        """Parse http."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # Sequence
        if state.pos != 0:
            raise ParseError("expected start of input")
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        # Repeat: match as many occurrences as we can
        children1: list[Pair] = []
        while True:
            state.checkpoint()
            try:
                # Choice: expression | expression
                children2: list[Pair] = []
                matched3 = False
                if not matched3:
                    state.checkpoint()
                    try:
                        children2.extend(parse_delimiter(state))
                        matched3 = True
                        state.ok()
                    except ParseError:
                        state.restore()
                        children2.clear()
                if not matched3:
                    state.checkpoint()
                    try:
                        children2.extend(parse_request(state))
                        matched3 = True
                        state.ok()
                    except ParseError:
                        state.restore()
                        children2.clear()
                if not matched3:
                    raise ParseError("no choice matched")
                children1.extend(children2)
                parse_trivia(state, children1)
                state.ok()
            except ParseError:
                state.restore()
                break
        pairs.extend(children1)
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        if state.pos != len(state.input):
            raise ParseError("expected end of input")
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_http = _parse_http()


def _parse_request() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("request", 0)

    def inner(state: State) -> Pairs:
        """Parse request."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # Sequence
        pairs.extend(parse_request_line(state))
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        children1: list[Pair] = []
        state.checkpoint()
        try:
            children1.extend(parse_headers(state))
            pairs.extend(children1)
            state.ok()
        except ParseError:
            state.restore()
            children1.clear()
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        # Choice: expression | expression
        children2: list[Pair] = []
        matched3 = False
        if not matched3:
            state.checkpoint()
            try:
                if state.input.startswith("\n", state.pos):
                    state.pos += 1
                else:
                    raise ParseError("\n")
                matched3 = True
                state.ok()
            except ParseError:
                state.restore()
                children2.clear()
        if not matched3:
            state.checkpoint()
            try:
                if state.input.startswith("\r\n", state.pos):
                    state.pos += 2
                else:
                    raise ParseError("\r\n")
                matched3 = True
                state.ok()
            except ParseError:
                state.restore()
                children2.clear()
        if not matched3:
            state.checkpoint()
            try:
                if state.input.startswith("\r", state.pos):
                    state.pos += 1
                else:
                    raise ParseError("\r")
                matched3 = True
                state.ok()
            except ParseError:
                state.restore()
                children2.clear()
        if not matched3:
            raise ParseError("no choice matched")
        pairs.extend(children2)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_request = _parse_request()


def _parse_request_line() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("request_line", 2)

    def inner(state: State) -> Pairs:
        """Parse request_line."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # Sequence
        pairs.extend(parse_method(state))
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        # RepeatOnce: attempt to match at least one occurrence
        children1: list[Pair] = []
        count2 = 0
        while True:
            state.checkpoint()
            try:
                if state.input.startswith(" ", state.pos):
                    state.pos += 1
                else:
                    raise ParseError(" ")
                count2 += 1
                state.ok()
                parse_trivia(state, children1)
            except ParseError:
                state.restore()
                break
        if count2 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children1)
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        pairs.extend(parse_uri(state))
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        # RepeatOnce: attempt to match at least one occurrence
        children3: list[Pair] = []
        count4 = 0
        while True:
            state.checkpoint()
            try:
                if state.input.startswith(" ", state.pos):
                    state.pos += 1
                else:
                    raise ParseError(" ")
                count4 += 1
                state.ok()
                parse_trivia(state, children3)
            except ParseError:
                state.restore()
                break
        if count4 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children3)
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        if state.input.startswith("HTTP/", state.pos):
            state.pos += 5
        else:
            raise ParseError("HTTP/")
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        pairs.extend(parse_version(state))
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        # Choice: expression | expression
        children5: list[Pair] = []
        matched6 = False
        if not matched6:
            state.checkpoint()
            try:
                if state.input.startswith("\n", state.pos):
                    state.pos += 1
                else:
                    raise ParseError("\n")
                matched6 = True
                state.ok()
            except ParseError:
                state.restore()
                children5.clear()
        if not matched6:
            state.checkpoint()
            try:
                if state.input.startswith("\r\n", state.pos):
                    state.pos += 2
                else:
                    raise ParseError("\r\n")
                matched6 = True
                state.ok()
            except ParseError:
                state.restore()
                children5.clear()
        if not matched6:
            state.checkpoint()
            try:
                if state.input.startswith("\r", state.pos):
                    state.pos += 1
                else:
                    raise ParseError("\r")
                matched6 = True
                state.ok()
            except ParseError:
                state.restore()
                children5.clear()
        if not matched6:
            raise ParseError("no choice matched")
        pairs.extend(children5)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_request_line = _parse_request_line()


def _parse_uri() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("uri", 0)

    def inner(state: State) -> Pairs:
        """Parse uri."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # RepeatOnce: attempt to match at least one occurrence
        children1: list[Pair] = []
        count2 = 0
        while True:
            state.checkpoint()
            try:
                # Sequence
                # NegativePredicate: !expression
                children3: list[Pair] = []
                state.checkpoint()
                try:
                    children3.extend(parse_whitespace(state))
                except ParseError:
                    state.restore()
                    children3.clear()  # discard lookahead children
                else:
                    state.restore()
                    raise ParseError("unexpected Identifier")
                # Implicit whitespace/comments between sequence elements
                parse_trivia(state, children1)
                if state.pos < len(state.input):
                    state.pos += 1
                else:
                    raise ParseError("unexpected end of input")
                count2 += 1
                state.ok()
                parse_trivia(state, children1)
            except ParseError:
                state.restore()
                break
        if count2 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_uri = _parse_uri()


def _parse_method() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("method", 0)

    def inner(state: State) -> Pairs:
        """Parse method."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # Choice: expression | expression
        children1: list[Pair] = []
        matched2 = False
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("GET", state.pos):
                    state.pos += 3
                else:
                    raise ParseError("GET")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("DELETE", state.pos):
                    state.pos += 6
                else:
                    raise ParseError("DELETE")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("POST", state.pos):
                    state.pos += 4
                else:
                    raise ParseError("POST")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("PUT", state.pos):
                    state.pos += 3
                else:
                    raise ParseError("PUT")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            raise ParseError("no choice matched")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_method = _parse_method()


def _parse_version() -> Callable[[State], Pairs]:
    RE5 = re.compile("\\[0\\-9\\]", re.I)

    rule_frame = RuleFrame("version", 0)

    def inner(state: State) -> Pairs:
        """Parse version."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # RepeatOnce: attempt to match at least one occurrence
        children1: list[Pair] = []
        count2 = 0
        while True:
            state.checkpoint()
            try:
                # Choice: expression | expression
                children3: list[Pair] = []
                matched4 = False
                if not matched4:
                    state.checkpoint()
                    try:
                        # Range: start..stop
                        if match := RE5.match(state.input, state.pos):
                            state.pos = match.end()
                        else:
                            raise ParseError("expected '0'..'9'")
                        matched4 = True
                        state.ok()
                    except ParseError:
                        state.restore()
                        children3.clear()
                if not matched4:
                    state.checkpoint()
                    try:
                        if state.input.startswith(".", state.pos):
                            state.pos += 1
                        else:
                            raise ParseError(".")
                        matched4 = True
                        state.ok()
                    except ParseError:
                        state.restore()
                        children3.clear()
                if not matched4:
                    raise ParseError("no choice matched")
                children1.extend(children3)
                count2 += 1
                state.ok()
                parse_trivia(state, children1)
            except ParseError:
                state.restore()
                break
        if count2 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_version = _parse_version()


def _parse_whitespace() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("whitespace", 2)

    def inner(state: State) -> Pairs:
        """Parse whitespace."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # Choice: expression | expression
        children1: list[Pair] = []
        matched2 = False
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith(" ", state.pos):
                    state.pos += 1
                else:
                    raise ParseError(" ")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("\t", state.pos):
                    state.pos += 1
                else:
                    raise ParseError("\t")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            raise ParseError("no choice matched")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_whitespace = _parse_whitespace()


def _parse_headers() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("headers", 0)

    def inner(state: State) -> Pairs:
        """Parse headers."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # RepeatOnce: attempt to match at least one occurrence
        children1: list[Pair] = []
        count2 = 0
        while True:
            state.checkpoint()
            try:
                children1.extend(parse_header(state))
                count2 += 1
                state.ok()
                parse_trivia(state, children1)
            except ParseError:
                state.restore()
                break
        if count2 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_headers = _parse_headers()


def _parse_header() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("header", 0)

    def inner(state: State) -> Pairs:
        """Parse header."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # Sequence
        pairs.extend(parse_header_name(state))
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        if state.input.startswith(":", state.pos):
            state.pos += 1
        else:
            raise ParseError(":")
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        pairs.extend(parse_whitespace(state))
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        pairs.extend(parse_header_value(state))
        # Implicit whitespace/comments between sequence elements
        parse_trivia(state, pairs)
        # Choice: expression | expression
        children1: list[Pair] = []
        matched2 = False
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("\n", state.pos):
                    state.pos += 1
                else:
                    raise ParseError("\n")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("\r\n", state.pos):
                    state.pos += 2
                else:
                    raise ParseError("\r\n")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            state.checkpoint()
            try:
                if state.input.startswith("\r", state.pos):
                    state.pos += 1
                else:
                    raise ParseError("\r")
                matched2 = True
                state.ok()
            except ParseError:
                state.restore()
                children1.clear()
        if not matched2:
            raise ParseError("no choice matched")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_header = _parse_header()


def _parse_header_name() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("header_name", 0)

    def inner(state: State) -> Pairs:
        """Parse header_name."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # RepeatOnce: attempt to match at least one occurrence
        children1: list[Pair] = []
        count2 = 0
        while True:
            state.checkpoint()
            try:
                # Sequence
                # NegativePredicate: !expression
                children3: list[Pair] = []
                state.checkpoint()
                try:
                    # Choice: expression | expression
                    children4: list[Pair] = []
                    matched5 = False
                    if not matched5:
                        state.checkpoint()
                        try:
                            # Choice: expression | expression
                            children6: list[Pair] = []
                            matched7 = False
                            if not matched7:
                                state.checkpoint()
                                try:
                                    if state.input.startswith("\n", state.pos):
                                        state.pos += 1
                                    else:
                                        raise ParseError("\n")
                                    matched7 = True
                                    state.ok()
                                except ParseError:
                                    state.restore()
                                    children6.clear()
                            if not matched7:
                                state.checkpoint()
                                try:
                                    if state.input.startswith("\r\n", state.pos):
                                        state.pos += 2
                                    else:
                                        raise ParseError("\r\n")
                                    matched7 = True
                                    state.ok()
                                except ParseError:
                                    state.restore()
                                    children6.clear()
                            if not matched7:
                                state.checkpoint()
                                try:
                                    if state.input.startswith("\r", state.pos):
                                        state.pos += 1
                                    else:
                                        raise ParseError("\r")
                                    matched7 = True
                                    state.ok()
                                except ParseError:
                                    state.restore()
                                    children6.clear()
                            if not matched7:
                                raise ParseError("no choice matched")
                            children4.extend(children6)
                            matched5 = True
                            state.ok()
                        except ParseError:
                            state.restore()
                            children4.clear()
                    if not matched5:
                        state.checkpoint()
                        try:
                            if state.input.startswith(":", state.pos):
                                state.pos += 1
                            else:
                                raise ParseError(":")
                            matched5 = True
                            state.ok()
                        except ParseError:
                            state.restore()
                            children4.clear()
                    if not matched5:
                        raise ParseError("no choice matched")
                    children3.extend(children4)
                except ParseError:
                    state.restore()
                    children3.clear()  # discard lookahead children
                else:
                    state.restore()
                    raise ParseError("unexpected Group")
                # Implicit whitespace/comments between sequence elements
                parse_trivia(state, children1)
                if state.pos < len(state.input):
                    state.pos += 1
                else:
                    raise ParseError("unexpected end of input")
                count2 += 1
                state.ok()
                parse_trivia(state, children1)
            except ParseError:
                state.restore()
                break
        if count2 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_header_name = _parse_header_name()


def _parse_header_value() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("header_value", 0)

    def inner(state: State) -> Pairs:
        """Parse header_value."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # RepeatOnce: attempt to match at least one occurrence
        children1: list[Pair] = []
        count2 = 0
        while True:
            state.checkpoint()
            try:
                # Sequence
                # NegativePredicate: !expression
                children3: list[Pair] = []
                state.checkpoint()
                try:
                    # Choice: expression | expression
                    children4: list[Pair] = []
                    matched5 = False
                    if not matched5:
                        state.checkpoint()
                        try:
                            if state.input.startswith("\n", state.pos):
                                state.pos += 1
                            else:
                                raise ParseError("\n")
                            matched5 = True
                            state.ok()
                        except ParseError:
                            state.restore()
                            children4.clear()
                    if not matched5:
                        state.checkpoint()
                        try:
                            if state.input.startswith("\r\n", state.pos):
                                state.pos += 2
                            else:
                                raise ParseError("\r\n")
                            matched5 = True
                            state.ok()
                        except ParseError:
                            state.restore()
                            children4.clear()
                    if not matched5:
                        state.checkpoint()
                        try:
                            if state.input.startswith("\r", state.pos):
                                state.pos += 1
                            else:
                                raise ParseError("\r")
                            matched5 = True
                            state.ok()
                        except ParseError:
                            state.restore()
                            children4.clear()
                    if not matched5:
                        raise ParseError("no choice matched")
                    children3.extend(children4)
                except ParseError:
                    state.restore()
                    children3.clear()  # discard lookahead children
                else:
                    state.restore()
                    raise ParseError("unexpected BuiltInRule")
                # Implicit whitespace/comments between sequence elements
                parse_trivia(state, children1)
                if state.pos < len(state.input):
                    state.pos += 1
                else:
                    raise ParseError("unexpected end of input")
                count2 += 1
                state.ok()
                parse_trivia(state, children1)
            except ParseError:
                state.restore()
                break
        if count2 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_header_value = _parse_header_value()


def _parse_delimiter() -> Callable[[State], Pairs]:
    rule_frame = RuleFrame("delimiter", 0)

    def inner(state: State) -> Pairs:
        """Parse delimiter."""
        state.rule_stack.push(rule_frame)
        pairs: list[Pair] = []
        # RepeatOnce: attempt to match at least one occurrence
        children1: list[Pair] = []
        count2 = 0
        while True:
            state.checkpoint()
            try:
                # Choice: expression | expression
                children3: list[Pair] = []
                matched4 = False
                if not matched4:
                    state.checkpoint()
                    try:
                        if state.input.startswith("\n", state.pos):
                            state.pos += 1
                        else:
                            raise ParseError("\n")
                        matched4 = True
                        state.ok()
                    except ParseError:
                        state.restore()
                        children3.clear()
                if not matched4:
                    state.checkpoint()
                    try:
                        if state.input.startswith("\r\n", state.pos):
                            state.pos += 2
                        else:
                            raise ParseError("\r\n")
                        matched4 = True
                        state.ok()
                    except ParseError:
                        state.restore()
                        children3.clear()
                if not matched4:
                    state.checkpoint()
                    try:
                        if state.input.startswith("\r", state.pos):
                            state.pos += 1
                        else:
                            raise ParseError("\r")
                        matched4 = True
                        state.ok()
                    except ParseError:
                        state.restore()
                        children3.clear()
                if not matched4:
                    raise ParseError("no choice matched")
                children1.extend(children3)
                count2 += 1
                state.ok()
                parse_trivia(state, children1)
            except ParseError:
                state.restore()
                break
        if count2 < 1:
            raise ParseError("Expected at least one match")
        pairs.extend(children1)
        state.rule_stack.pop()
        return Pairs(pairs)

    return inner


parse_delimiter = _parse_delimiter()


def parse_trivia(state: State, pairs: list[Pair]) -> None:
    pass
