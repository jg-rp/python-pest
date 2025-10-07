from abc import abstractmethod
from collections.abc import Callable


class Expression:
    """Base class for all expressions or sub expressions."""

    @abstractmethod
    def evaluate(self, variables: dict[str, int]) -> int:
        """Evaluate this expression."""


class VarExpr(Expression):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def evaluate(self, variables: dict[str, int]) -> int:
        return variables[self.value]


class IntExpr(Expression):
    def __init__(self, value: int) -> None:
        super().__init__()
        self.value = value

    def evaluate(self, variables: dict[str, int]) -> int:  # noqa: ARG002
        return self.value


class PrefixExpr(Expression):
    def __init__(self, op: Callable[[int], int], expr: Expression) -> None:
        super().__init__()
        self.op = op
        self.expr = expr

    def evaluate(self, variables: dict[str, int]) -> int:
        return self.op(self.expr.evaluate(variables))


class InfixExpr(Expression):
    def __init__(
        self, op: Callable[[int, int], int], left: Expression, right: Expression
    ) -> None:
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def evaluate(self, variables: dict[str, int]) -> int:
        return self.op(self.left.evaluate(variables), self.right.evaluate(variables))


class PostfixExpr(Expression):
    def __init__(self, op: Callable[[int], int], expr: Expression) -> None:
        super().__init__()
        self.op = op
        self.expr = expr

    def evaluate(self, variables: dict[str, int]) -> int:
        return self.op(self.expr.evaluate(variables))
