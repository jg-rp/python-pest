import pytest

from pest import DEFAULT_OPTIMIZER_PASSES
from pest import Optimizer
from pest import Parser
from pest.grammar import SkipUntil
from pest.grammar import parse


@pytest.fixture
def optimizer() -> Optimizer:
    return Optimizer(DEFAULT_OPTIMIZER_PASSES)


def test_skip_until(optimizer: Optimizer) -> None:
    rules, _ = parse('rule = { (!"\n" ~ ANY)* }', Parser.BUILTIN)
    want = SkipUntil(["\n"])
    optimizer.optimize(rules, debug=True)
    assert len(optimizer.log) == 1
    assert rules["rule"].expression == want


# def test_skip_until_negpred_choice(optimizer: Optimizer) -> None:
#     rules, _ = parse('rule = { (!("a" | "b") ~ ANY)* }', {})
#     want = SkipUntil(["a", "b"])
#     optimized = optimizer.optimize(rules, debug=True)
#     assert len(optimizer.log) == 1
#     assert optimized["rule"].expression == want
