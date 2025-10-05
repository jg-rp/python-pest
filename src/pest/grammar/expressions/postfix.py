"""pest postfix operators."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar import Expression
from pest.grammar.expression import Match

if TYPE_CHECKING:
    from pest.grammar.codegen.builder import Builder
    from pest.state import ParserState


class Optional(Expression):
    """A optional pest grammar expression.

    This corresponds to the `?` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        super().__init__(None)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.expression}?"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Optional) and self.expression == other.expression

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`.

        Args:
            state: The current parser state, including input text and
                   any memoization or error-tracking structures.
            start: The index in the input string where parsing begins.
        """
        matches = state.parse(self.expression, start, self.tag)
        if matches:
            return matches
        return [Match(None, start)]

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python source code that implements this grammar expression."""
        gen.writeln("# <Optional>")
        tmp_pairs = gen.new_temp("children")

        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln("state.checkpoint()")

        self.expression.generate(gen, matched_var, tmp_pairs)

        gen.writeln(f"if {matched_var}:")
        with gen.block():
            gen.writeln("state.ok()")
            gen.writeln(f"{pairs_var}.extend({tmp_pairs})")
        gen.writeln("else:")
        with gen.block():
            gen.writeln("state.restore()")
            gen.writeln(f"{tmp_pairs}.clear()")

        gen.writeln("# </Optional>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)


class Repeat(Expression):
    """A pest grammar expression repeated zero or more times.

    This corresponds to the `*` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        super().__init__(None)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.expression}*"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Repeat) and self.expression == other.expression

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        position = start
        matched = False
        matches: list[Match] = []

        while True:
            state.snapshot()
            results = state.parse(self.expression, position, self.tag)

            if not results:
                state.restore()
                break

            matched = True
            position = results[-1].pos
            state.ok()
            matches.extend(results)

            for match in state.parse_implicit_rules(position):
                position = match.pos
                matches.append(match)

        # Always succeed.
        if not matched:
            return [Match(None, position)]
        return matches

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for repeat zero or more times."""
        gen.writeln("# <Repeat>")

        tmp_pairs = gen.new_temp("children")
        trivia_pos = gen.new_temp("trivia_pos")

        gen.writeln(f"{trivia_pos} = state.pos")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")

        gen.writeln("while True:")
        with gen.block():
            gen.writeln("state.checkpoint()")
            # Parse one item
            self.expression.generate(gen, matched_var, tmp_pairs)

            gen.writeln(f"if {matched_var}:")
            with gen.block():
                gen.writeln("state.ok()")
                # Commit the item immediately
                gen.writeln(f"{pairs_var}.extend({tmp_pairs})")
                gen.writeln(f"{tmp_pairs}.clear()")
                # Save pos before trivia
                gen.writeln(f"{trivia_pos} = state.pos")
                # Parse trivia after item
                gen.writeln(f"parse_trivia(state, {tmp_pairs})")
            gen.writeln("else:")
            with gen.block():
                # Restore checkpoint and also rewind trivia pos
                gen.writeln("state.restore()")
                gen.writeln(f"state.pos = {trivia_pos}")
                # Always succeed
                gen.writeln(f"{matched_var} = True")
                gen.writeln("break")

        gen.writeln("# </Repeat>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)


class RepeatOnce(Expression):
    """A pest grammar expression repeated one or more times.

    This corresponds to the `+` operator in pest.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expression):
        super().__init__(None)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.tag_str()}{self.expression}+"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        state.snapshot()
        matches = state.parse(self.expression, start, self.tag)

        if not matches:
            state.restore()
            return None

        state.ok()
        position = matches[-1].pos

        for success in state.parse_implicit_rules(position):
            position = success.pos
            matches.append(success)

        while True:
            state.snapshot()
            results = state.parse(self.expression, position, self.tag)
            if not results:
                state.restore()
                break
            position = results[-1].pos
            state.ok()
            matches.extend(results)

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        return matches

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for repeat one or more times."""
        gen.writeln("# <RepeatOnce>")
        acc_pairs = gen.new_temp("children")
        tmp_pairs = gen.new_temp("item_children")
        count_var = gen.new_temp("count")
        trivia_pos = gen.new_temp("trivia_pos")
        gen.writeln(f"{trivia_pos} = state.pos")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")

        gen.writeln(f"{count_var} = 0")
        gen.writeln("while True:")
        with gen.block():
            gen.writeln("state.checkpoint()")
            # Parse one item
            self.expression.generate(gen, matched_var, tmp_pairs)

            gen.writeln(f"if {matched_var}:")
            with gen.block():
                gen.writeln(f"{count_var} += 1")
                gen.writeln("state.ok()")

                # Commit the item immediately
                gen.writeln(f"{acc_pairs}.extend({tmp_pairs})")
                gen.writeln(f"{tmp_pairs}.clear()")

                # Save pos before trivia
                gen.writeln(f"{trivia_pos} = state.pos")

                # Parse trivia after item.
                # Non-silent trivia will be added to acc_pairs on the next
                # iteration if it succeeds.
                gen.writeln(f"parse_trivia(state, {tmp_pairs})")

            gen.writeln("else:")
            with gen.block():
                # Restore checkpoint and also rewind trivia pos
                gen.writeln("state.restore()")
                gen.writeln(f"state.pos = {trivia_pos}")
                gen.writeln("break")

        # After the loop, validate minimum
        gen.writeln(f"if {count_var} < 1:")
        with gen.block():
            gen.writeln(f"{matched_var} = False")
        gen.writeln("else:")
        with gen.block():
            gen.writeln(f"{pairs_var}.extend({acc_pairs})")
            gen.writeln(f"{matched_var} = True")

        gen.writeln("# </RepeatOnce>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(*expressions)


class RepeatExact(Expression):
    """A pest grammar expression repeated a specified number of times.

    This corresponds to the `{n}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int):
        super().__init__(None)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.expression}{{{self.number}}}"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = state.parse(self.expression, position, self.tag)

            if not results:
                break

            position = results[-1].pos
            matches.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        if match_count == self.number:
            state.ok()
            return matches

        state.restore()
        return None

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a bounded repetition expression (E{num})."""
        gen.writeln(f"# <RepeatExact n={self.number}>")

        start_pos = gen.new_temp("start")
        tmp_pairs = gen.new_temp("children")
        count_var = gen.new_temp("count")

        gen.writeln(f"{start_pos} = state.pos")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln(f"{count_var} = 0")

        gen.writeln("while True:")
        with gen.block():
            gen.writeln("state.checkpoint()")
            self.expression.generate(gen, matched_var, tmp_pairs)

            gen.writeln(f"if {matched_var}:")
            with gen.block():
                gen.writeln(f"{count_var} += 1")
                gen.writeln("state.ok()")
                # Stop if we've already reached the maximum
                gen.writeln(f"if {count_var} >= {self.number}:")
                with gen.block():
                    gen.writeln("break")
                gen.writeln(f"parse_trivia(state, {tmp_pairs})")
            gen.writeln("else:")
            with gen.block():
                gen.writeln("state.restore()")
                gen.writeln("break")

        # After the loop, validate minimum
        gen.writeln(f"if {count_var} < {self.number}:")
        with gen.block():
            gen.writeln(f"state.pos = {start_pos}")
            gen.writeln(f"{matched_var} = False")
        gen.writeln("else:")
        with gen.block():
            # Append successful children to the parent pair list
            gen.writeln(f"{pairs_var}.extend({tmp_pairs})")

        gen.writeln("# </RepeatExact>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.number)


class RepeatMin(Expression):
    """A pest grammar expression repeated at least a specified number of times.

    This corresponds to the `{n,}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int):
        super().__init__(None)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.expression}{{{self.number},}}"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = state.parse(self.expression, position, self.tag)
            if not results:
                break
            position = results[-1].pos
            matches.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        if match_count >= self.number:
            state.ok()
            return matches

        state.restore()
        return None

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a bounded repetition expression (E{min,})."""
        gen.writeln(f"# <RepeatMin n={self.number}>")

        start_pos = gen.new_temp("start")
        tmp_pairs = gen.new_temp("children")
        count_var = gen.new_temp("count")

        gen.writeln(f"{start_pos} = state.pos")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln(f"{count_var} = 0")

        gen.writeln("while True:")
        with gen.block():
            gen.writeln("state.checkpoint()")
            self.expression.generate(gen, matched_var, tmp_pairs)
            gen.writeln(f"if {matched_var}:")
            with gen.block():
                gen.writeln(f"{count_var} += 1")
                gen.writeln("state.ok()")
                # TODO: backtrack last trivia
                gen.writeln(f"parse_trivia(state, {tmp_pairs})")
            gen.writeln("else:")
            with gen.block():
                gen.writeln("state.restore()")
                gen.writeln("break")

        # After the loop, validate minimum
        gen.writeln(f"if {count_var} < {self.number}:")
        with gen.block():
            gen.writeln(f"state.pos = {start_pos}")
            gen.writeln(f"{matched_var} = False")

        # Append successful children to the parent pair list
        gen.writeln(f"{pairs_var}.extend({tmp_pairs})")
        gen.writeln("# </RepeatMin>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.number)


class RepeatMax(Expression):
    """A pest grammar expression repeated at most a specified number of times.

    This corresponds to the `{,n}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "number",
    )

    def __init__(self, expression: Expression, number: int):
        super().__init__(None)
        self.expression = expression
        self.number = number

    def __str__(self) -> str:
        return f"{self.expression}{{,{self.number}}}"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        position = start
        state.snapshot()

        for i in range(self.number):
            results = state.parse(self.expression, position, self.tag)
            if not results:
                break

            position = results[-1].pos
            matches.extend(results)

            if i < self.number - 1:
                for success in state.parse_implicit_rules(position):
                    position = success.pos
                    matches.append(success)

        if matches:
            state.ok()
            return matches

        state.restore()
        return None

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a bounded repetition expression (E{,max})."""
        gen.writeln(f"# <RepeatMax n={self.number}>")

        tmp_pairs = gen.new_temp("children")
        count_var = gen.new_temp("count")

        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln(f"{count_var} = 0")

        gen.writeln("while True:")
        with gen.block():
            gen.writeln("state.checkpoint()")
            self.expression.generate(gen, matched_var, tmp_pairs)
            gen.writeln(f"if {matched_var}:")
            with gen.block():
                gen.writeln(f"{count_var} += 1")
                gen.writeln("state.ok()")
                # Stop if we've already reached the maximum
                gen.writeln(f"if {count_var} >= {self.number}:")
                with gen.block():
                    gen.writeln("break")
                gen.writeln(f"parse_trivia(state, {tmp_pairs})")
            gen.writeln("else:")
            with gen.block():
                gen.writeln("state.restore()")
                gen.writeln("break")

        # Append successful children to the parent pair list
        gen.writeln(f"{pairs_var}.extend({tmp_pairs})")
        gen.writeln("# </RepeatMax>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.number)


class RepeatMinMax(Expression):
    """A pest grammar expression repeated a specified range of times.

    This corresponds to the `{n,m}` postfix expression in pest.
    """

    __slots__ = (
        "expression",
        "min",
        "max",
    )

    def __init__(self, expression: Expression, min_: int, max_: int):
        super().__init__(None)
        self.expression = expression
        self.min = min_
        self.max = max_

    def __str__(self) -> str:
        return f"{self.expression}{{{self.min}, {self.max}}}"

    def parse(self, state: ParserState, start: int) -> list[Match] | None:
        """Attempt to match this expression against the input at `start`."""
        matches: list[Match] = []
        match_count = 0
        position = start
        state.snapshot()

        while True:
            results = state.parse(self.expression, position, self.tag)
            if not results:
                break
            position = results[-1].pos
            matches.extend(results)
            match_count += 1

            for success in state.parse_implicit_rules(position):
                position = success.pos
                matches.append(success)

        if match_count >= self.min and match_count <= self.max:
            state.ok()
            return matches

        state.restore()
        return None

    def generate(self, gen: Builder, matched_var: str, pairs_var: str) -> None:
        """Emit Python code for a bounded repetition expression (E{min,max})."""
        gen.writeln(f"# <RepeatMinMax min={self.min} max={self.max}>")

        start_pos = gen.new_temp("start")
        tmp_pairs = gen.new_temp("children")
        count_var = gen.new_temp("count")

        gen.writeln(f"{start_pos} = state.pos")
        gen.writeln(f"{tmp_pairs}: list[Pair] = []")
        gen.writeln(f"{count_var} = 0")

        gen.writeln("while True:")
        with gen.block():
            gen.writeln("state.checkpoint()")
            self.expression.generate(gen, matched_var, tmp_pairs)
            gen.writeln(f"if {matched_var}:")
            with gen.block():
                gen.writeln(f"{count_var} += 1")
                gen.writeln("state.ok()")
                # Stop if we've already reached the maximum
                gen.writeln(f"if {count_var} >= {self.max}:")
                with gen.block():
                    gen.writeln("break")
                gen.writeln(f"parse_trivia(state, {tmp_pairs})")
            gen.writeln("else:")
            with gen.block():
                gen.writeln("state.restore()")
                gen.writeln("break")

        gen.writeln(f"if {count_var} < {self.min}:")
        with gen.block():
            gen.writeln(f"state.pos = {start_pos}")
            gen.writeln(f"{matched_var} = False")

        # Append successful children to the parent pair list
        gen.writeln(f"{pairs_var}.extend({tmp_pairs})")
        gen.writeln("# </RepeatMinMax>")

    def children(self) -> list[Expression]:
        """Return this expression's children."""
        return [self.expression]

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        return self.__class__(expressions[0], self.min, self.max)
