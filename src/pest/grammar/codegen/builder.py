from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


class Builder:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.indent = 0
        self.temp_counter = 0

    def writeln(self, line: str = "") -> None:
        self.lines.append("    " * self.indent + line)

    @contextmanager
    def block(self) -> Iterator[Builder]:
        self.indent += 1
        yield self
        self.indent -= 1

    def new_temp(self, prefix: str = "_tmp") -> str:
        self.temp_counter += 1
        return f"{prefix}{self.temp_counter}"

    def render(self) -> str:
        return "\n".join(self.lines)
