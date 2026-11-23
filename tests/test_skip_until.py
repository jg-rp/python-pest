import pytest

from pest import DEFAULT_OPTIMIZER_PASSES, Optimizer, Parser
from pest.grammar import SkipUntil, parse


@pytest.fixture
def optimizer() -> Optimizer:
    return Optimizer(DEFAULT_OPTIMIZER_PASSES)


def test_skip_until_neg_pred_literal(optimizer: Optimizer) -> None:
    rules, _ = parse('rule = { (!"\n" ~ ANY)* }', Parser.BUILTIN)
    want = SkipUntil(["\n"])
    optimizer.optimize(rules, debug=True)
    assert rules["rule"].expression == want


def test_skip_until_neg_pred_choice(optimizer: Optimizer) -> None:
    rules, _ = parse('rule = { (!("a" | "b") ~ ANY)* }', Parser.BUILTIN)
    want = SkipUntil(["a", "b"])
    optimizer.optimize(rules, debug=True)
    assert rules["rule"].expression == want


def test_skip_until_neg_pred_identifier(optimizer: Optimizer) -> None:
    rules, _ = parse('foo = { "a" | "b" }\nrule = { (!foo ~ ANY)* }', Parser.BUILTIN)
    want = SkipUntil(["a", "b"])
    optimizer.optimize(rules, debug=True)
    assert rules["rule"].expression == want
