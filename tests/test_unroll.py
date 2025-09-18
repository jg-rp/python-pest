import pytest

from pest import DEFAULT_OPTIMIZER_PASSES
from pest import Optimizer
from pest import Parser
from pest.grammar import Identifier
from pest.grammar import Optional
from pest.grammar import Repeat
from pest.grammar import Sequence
from pest.grammar import String
from pest.grammar import parse


@pytest.fixture
def optimizer() -> Optimizer:
    return Optimizer(DEFAULT_OPTIMIZER_PASSES)


def test_unroll_loop_exact(optimizer: Optimizer) -> None:
    rules, _ = parse("rule = { a{3} }", Parser.BUILTIN)
    want = Sequence(Identifier("a"), Identifier("a"), Identifier("a"))
    optimizer.optimize(rules, debug=True)
    assert len(optimizer.log) == 1
    assert rules["rule"].expression == want


def test_unroll_loop_max(optimizer: Optimizer) -> None:
    rules, _ = parse('rule = { "a"{,3} }', Parser.BUILTIN)
    want = Sequence(
        Optional(String("a")),
        Optional(String("a")),
        Optional(String("a")),
    )
    optimizer.optimize(rules, debug=True)
    assert len(optimizer.log) == 1
    assert rules["rule"].expression == want


def test_unroll_loop_min(optimizer: Optimizer) -> None:
    rules, _ = parse('rule = { "a"{2,} }', Parser.BUILTIN)
    want = Sequence(
        String("a"),
        String("a"),
        Repeat(String("a")),
    )
    optimizer.optimize(rules, debug=True)
    assert len(optimizer.log) == 1
    assert rules["rule"].expression == want


def test_unroll_loop_min_max(optimizer: Optimizer) -> None:
    rules, _ = parse('rule = { "a"{2,3} }', Parser.BUILTIN)
    want = Sequence(
        String("a"),
        String("a"),
        Optional(String("a")),
    )
    optimizer.optimize(rules, debug=True)
    assert len(optimizer.log) == 1
    assert rules["rule"].expression == want


def test_unroll_loop_repeat_once(optimizer: Optimizer) -> None:
    rules, _ = parse('rule = { "a"+ }', Parser.BUILTIN)
    want = Sequence(
        String("a"),
        Repeat(String("a")),
    )
    optimizer.optimize(rules, debug=True)
    assert len(optimizer.log) == 1
    assert rules["rule"].expression == want
