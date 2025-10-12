"""Terminal expressions."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING
from typing import Self

import regex as re

from pest.grammar.expression import Expression
from pest.grammar.expression import Terminal

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.grammar.rule import Rule
    from pest.pairs import Pair
    from pest.state import ParserState


class PushLiteral(Terminal):
    """A PUSH terminal with a string literal argument."""

    __slots__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f'{self.tag_str()}PUSH("{self.value}")'

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        state.push(self.value)
        return True

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a PUSH expression."""
        gen.writeln("# <PushLiteral>")
        gen.writeln(f"state.push({self.value!r})")
        gen.writeln(f"{matched_var} = True")
        gen.writeln("# </PushLiteral>")

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


# TODO: PUSH(expression) is not terminal


class Push(Expression):
    """A PUSH terminal with an expression."""

    __slots__ = ("expression",)

    def __init__(self, expression: Expression, tag: str | None = None):
        super().__init__(tag)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}PUSH( {self.expression} )"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        start = state.pos
        children: list[Pair] = []
        matched = self.expression.parse(state, children)

        if not matched:
            return False

        state.push(state.input[start : state.pos])
        pairs.extend(children)
        return True

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a PUSH expression."""
        gen.writeln("# <Push>")

        start_var = gen.new_temp("start")
        gen.writeln(f"{start_var} = state.pos")
        # TODO: Can PUSH(<expr>) fail?
        # TODO: snapshot and tmp_pairs?
        # TODO: test for failed PUSH
        self.expression.generate(gen, matched_var, pairs_var)

        gen.writeln(f"if {matched_var}:")
        with gen.block():
            gen.writeln(f"state.push(state.input[{start_var} : state.pos])")

        gen.writeln("# </Push>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.tag)

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class PeekSlice(Terminal):
    """A PEEK terminal with a range expression.

    Matches the range from the bottom of the stack to the top.
    """

    __slots__ = ("start", "stop")

    def __init__(
        self,
        start: str | None = None,
        stop: str | None = None,
        tag: str | None = None,
    ):
        super().__init__(tag)
        self.start = int(start) if start else None
        self.stop = int(stop) if stop else None

    def __str__(self) -> str:
        start = self.start if self.start else ""
        stop = self.stop if self.stop else ""
        return f"{self.tag_str()}PEEK[{start}..{stop}]"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        position = state.pos

        for literal in state.peek_slice(self.start, self.stop):
            if state.input.startswith(literal, position):
                position += len(literal)
            else:
                state.fail(literal)
                return False

        state.pos = position
        return True

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a PEEK expression."""
        gen.writeln("# <PeekSlice>")

        pos = gen.new_temp("pos")
        gen.writeln(f"{pos} = state.pos")
        peeked = gen.new_temp("peek")
        gen.writeln(f"for {peeked} in state.peek_slice({self.start}, {self.stop}):")
        with gen.block():
            gen.writeln(f"if state.input.startswith({peeked}, {pos}):")
            with gen.block():
                gen.writeln(f"{pos} += len({peeked})")
                gen.writeln(f"{matched_var} = True")
            gen.writeln("else:")
            with gen.block():
                # TODO: test for failed PEEK slice
                gen.writeln(f"{matched_var} = False")
                gen.writeln(f"state.fail({peeked})")
                gen.writeln("break")

        gen.writeln(f"state.pos = {pos}")

        gen.writeln("# </PeekSlice>")

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class Peek(Terminal):
    """A PEEK terminal looking at the top of the stack."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}PEEK"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        with suppress(IndexError):
            value = state.user_stack.peek()

            if state.input.startswith(value, state.pos):
                state.pos += len(value)
                return True

            state.fail(value)
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a PEEK expression."""
        gen.writeln("# <Peek>")

        peeked = gen.new_temp("peek")
        gen.writeln(f"{peeked} = state.peek()")

        gen.writeln(
            f"if {peeked} is not None and state.input.startswith({peeked}, state.pos):"
        )
        with gen.block():
            gen.writeln(f"state.pos += len({peeked})")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
            gen.writeln(f"state.fail({peeked})")

        gen.writeln("# </Peek>")

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class PeekAll(Terminal):
    """A PEEK_ALL terminal match the entire stack, top to bottom."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}PEEK_ALL"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        position = state.pos
        stack_size = len(state.user_stack)
        children: list[Pair] = []

        for i, literal in enumerate(reversed(state.user_stack)):
            # XXX: can `literal` be empty?
            if not state.input.startswith(literal, position):
                state.fail(literal)
                return False

            position += len(literal)

            if i < stack_size:
                state.parse_trivia(children)

        state.pos = position
        pairs.extend(children)
        return True

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a PEEK_ALL expression."""
        gen.writeln("# <PeekAll>")

        start_var = gen.new_temp("start")
        tmp_pairs = gen.new_temp("pairs")

        gen.writeln(f"{start_var} = state.pos")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln(f"{matched_var} = True")

        gen.writeln("for i, literal in enumerate(reversed(state.user_stack)):")
        with gen.block():
            gen.writeln("if state.input.startswith(literal, state.pos):")
            with gen.block():
                gen.writeln("state.pos += len(literal)")
                gen.writeln(f"{matched_var} = True")
                gen.writeln("if i < len(state.user_stack):")
                with gen.block():
                    gen.writeln(f"parse_trivia(state, {tmp_pairs})")
            gen.writeln("else:")
            with gen.block():
                gen.writeln(f"state.pos = {start_var}")
                gen.writeln(f"{matched_var} = False")
                gen.writeln("state.fail(literal)")
                gen.writeln("break")

        gen.writeln("# </PeekAll>")

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class Pop(Terminal):
    """A POP terminal popping off the top of the stack."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}POP"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        with suppress(IndexError):
            value = state.user_stack.peek()
            if state.input.startswith(value, state.pos):
                state.user_stack.pop()
                state.pos += len(value)
                return True
            state.fail(value)
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a PEEK expression."""
        gen.writeln("# <Pop>")

        peeked = gen.new_temp("peek")
        gen.writeln(f"{peeked} = state.peek()")

        gen.writeln(
            f"if {peeked} is not None and state.input.startswith({peeked}, state.pos):"
        )
        with gen.block():
            gen.writeln("state.user_stack.pop()")
            gen.writeln(f"state.pos += len({peeked})")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
            gen.writeln(f"state.fail({peeked})")

        gen.writeln("# </Pop>")

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class PopAll(Terminal):
    """A POP_ALL terminal matching the entire stack, top to bottom."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}POP_ALL"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        position = state.pos
        children: list[Pair] = []
        state.checkpoint()

        while not state.user_stack.empty():
            literal = state.user_stack.pop()
            if not state.input.startswith(literal, position):
                state.restore()
                state.fail(literal)
                return False

            position += len(literal)

            # TODO: don't skip trivia after the last pop
            state.parse_trivia(children)

        state.ok()
        state.pos = position
        pairs.extend(children)
        return True

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a POP_ALL expression."""
        gen.writeln("# <PopAll>")

        pos = gen.new_temp("pos")
        gen.writeln(f"{pos} = state.pos")

        peeked = gen.new_temp("peek")
        gen.writeln(f"for {peeked} in reversed(state.user_stack):")
        with gen.block():
            gen.writeln(f"if state.input.startswith({peeked}, {pos}):")
            with gen.block():
                gen.writeln(f"{pos} += len({peeked})")
                gen.writeln(f"{matched_var} = True")
            gen.writeln("else:")
            with gen.block():
                gen.writeln(f"{matched_var} = False")
                gen.writeln(f"state.fail({peeked})")
                gen.writeln("break")

        gen.writeln("state.user_stack.clear()")
        gen.writeln(f"state.pos = {pos}")

        gen.writeln("# </PopAll>")

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


class Drop(Terminal):
    """A DROP terminal that matches if the stack is not empty."""

    __slots__ = ()

    def __str__(self) -> str:
        return f"{self.tag_str()}DROP"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        if not state.user_stack.empty():
            state.user_stack.pop()
            return True
        state.fail("drop from empty stack")
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a Drop expression."""
        gen.writeln("# <Drop>")

        gen.writeln("if not state.user_stack.empty():")
        with gen.block():
            gen.writeln("state.user_stack.pop()")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
            gen.writeln("state.fail('drop from empty stack')")

        gen.writeln("# <Drop>")

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        return False


# TODO: Identifier is not a terminal


class Identifier(Expression):
    """A terminal pointing to rule, possibly a built-in rule."""

    __slots__ = ("value",)
    __match_args__ = ("value",)

    def __init__(self, value: str, tag: str | None = None):
        super().__init__(tag)
        self.value = value

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.value}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Identifier) and other.value == self.value

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        # TODO: Handle unknown rule.
        assert state.parser
        if self.tag:
            with state.tag(self.tag):
                return state.parser.rules[self.value].parse(state, pairs)
        return state.parser.rules[self.value].parse(state, pairs)

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for calling another rule."""
        gen.writeln("# <Identifier>")

        if self.tag:
            gen.writeln(f"with state.tag({self.tag!r}):")
            with gen.block():
                gen.writeln(f"{matched_var} = parse_{self.value}(state, {pairs_var})")
        else:
            gen.writeln(f"{matched_var} = parse_{self.value}(state, {pairs_var})")

        gen.writeln("# </Identifier>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return []

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert not expressions
        return self

    def is_pure(self, rules: dict[str, Rule], seen: set[str] | None = None) -> bool:
        """True if the expression has no side effects and is safe for memoization."""
        seen = seen or set()
        if self.value not in seen and self._pure is None:
            seen.add(self.value)
            self._pure = rules[self.value].is_pure(rules, seen)
        return self._pure or False


class String(Terminal):
    """A terminal string literal."""

    __slots__ = ("value",)

    def __init__(self, value: str):
        super().__init__(None)
        self.value = value

    def __str__(self) -> str:
        # TODO: replace non-printing characters with \u{XXXX} escape sequence
        # TODO: escape literal `"`
        value = (
            self.value.replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")
        )
        return f'"{value}"'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, String) and self.value == other.value

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        if state.input.startswith(self.value, state.pos):
            state.pos += len(self.value)
            return True
        state.fail(str(self))
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python source code that implements this grammar expression."""
        gen.writeln("# <String>")

        lit_repr = repr(self.value)
        gen.writeln(f"if state.input.startswith({lit_repr}, state.pos):")
        with gen.block():
            gen.writeln(f"state.pos += {len(self.value)}")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
            gen.writeln(f"state.fail({str(self)!r})")

        gen.writeln("# </String>")


class CIString(Terminal):
    """A terminal string literal that matches case insensitively."""

    __slots__ = ("value", "_re")

    def __init__(self, value: str):
        super().__init__(None)
        # TODO: unescape value
        self.value = value
        self._re = re.compile(re.escape(value), re.I)

    def __str__(self) -> str:
        # TODO: replace non-printing characters with \u{XXXX} escape sequence
        value = (
            self.value.replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")
        )
        return f'{self.tag_str()}^"{value}"'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CIString) and self.value == other.value

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        if self._re.match(state.input, state.pos):
            state.pos += len(self.value)
            return True
        state.fail(str(self))
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a case insensitive string literal."""
        gen.writeln("# <CIString>")

        pattern = re.escape(self.value)
        re_var = gen.constant("RE", f"re.compile({pattern!r}, re.I)")

        gen.writeln(f"if match := {re_var}.match(state.input, state.pos):")
        with gen.block():
            gen.writeln("state.pos = match.end()")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
            gen.writeln(f"state.fail({str(self)!r})")

        gen.writeln("# </CIString>")


class Range(Terminal):
    """A terminal range of characters."""

    __slots__ = ("start", "stop", "_re")

    def __init__(self, start: str, stop: str, tag: str | None = None):
        super().__init__(tag)
        self.start = start
        self.stop = stop
        self._re = re.compile(rf"[{re.escape(self.start)}-{re.escape(self.stop)}]")

    def __str__(self) -> str:
        return f"{self.tag_str()}'{self.start!r}'..'{self.stop!r}'"

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        if match := self._re.match(state.input, state.pos):
            state.pos = match.end()
            return True
        state.fail(str(self))
        return False

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a character range."""
        gen.writeln("# <Range>")

        pattern = rf"[{re.escape(self.start)}-{re.escape(self.stop)}]"
        re_var = gen.constant("RE", f"re.compile({pattern!r}, re.I)")

        gen.writeln(f"if match := {re_var}.match(state.input, state.pos):")
        with gen.block():
            gen.writeln("state.pos = match.end()")
            gen.writeln(f"{matched_var} = True")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
            gen.writeln(f"state.fail({str(self)!r})")

        gen.writeln("# </Range>")


class SkipUntil(Terminal):
    """A terminal that matches characters until one of a set of substrings is found.

    Attributes:
        subs: The list of substrings that terminate the match.
    """

    __slots__ = ("subs",)

    def __init__(self, subs: list[str]):
        super().__init__(tag=None)
        self.subs = subs

    def __str__(self) -> str:
        _subs = [repr(s)[1:-1] for s in self.subs]
        strings = " | ".join(f'"{s}"' for s in _subs)
        return f"(!({strings}) ~ ANY)*"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SkipUntil) and other.subs == self.subs

    def parse(self, state: ParserState, pairs: list[Pair]) -> bool:  # noqa: D102
        """Attempt to match this expression against the input at `start`.

        The match consumes characters until the earliest occurrence of any of
        the substrings in `self.subs`.

        Notes:
            - Benchmarks show this simple "loop and find" implementation to be
              faster than an Aho-Corasick approach up to a couple hundred
              substrings (`len(self.subs)`).
        """
        best_index: int | None = None
        s = state.input

        for sub in self.subs:
            pos = s.find(sub, state.pos)
            if pos != -1 and (best_index is None or pos < best_index):
                best_index = pos

        if best_index is not None:
            state.pos = best_index
        else:
            state.pos = len(s)

        return True

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for an optimized rep/neg-pred/any expression."""
        gen.writeln("# <SkipUntil>")

        subs_var = gen.constant("SUBS", str(self.subs))
        sub_var = gen.new_temp("sub")
        index_var = gen.new_temp("idx")
        input_var = gen.new_temp("s")
        pos_var = gen.new_temp("pos")

        gen.writeln(f"{input_var} = state.input")
        gen.writeln(f"{index_var}: int | None = None")

        gen.writeln(f"for {sub_var} in {subs_var}:")
        with gen.block():
            gen.writeln(f"{pos_var} = {input_var}.find({sub_var}, state.pos)")
            gen.writeln(
                f"if {pos_var} != -1 and ({index_var} is None "
                f"or {pos_var} < {index_var}):"
            )
            with gen.block():
                gen.writeln(f"{index_var} = {pos_var}")

        gen.writeln(f"if {index_var} is not None:")
        with gen.block():
            gen.writeln(f"state.pos = {index_var}")
        gen.writeln("else:")
        with gen.block():
            gen.writeln("state.pos = len(state.input)")

        gen.writeln(f"{matched_var} = True")
        gen.writeln("# </SkipUntil>")
