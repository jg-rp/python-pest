import pytest
from _pytest.fixtures import SubRequest

from pest import DEFAULT_OPTIMIZER
from pest import Parser
from pest import PestParsingError


@pytest.fixture(scope="module", params=["not optimized", "optimized"])
def parser(request: SubRequest) -> Parser:
    optimizer = DEFAULT_OPTIMIZER if request.param == "optimized" else None
    with open("tests/grammars/reporting.pest", encoding="utf-8") as fd:
        return Parser.from_grammar(fd.read(), optimizer=optimizer)


def test_choices(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices", "x")

    err = exec_info.value
    assert err.positives == ["a", "b", "c"]
    assert err.negatives == []
    assert err.pos == 0


def test_choice_no_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_no_progress", "x")

    err = exec_info.value
    assert err.positives == ["a", "b", "c"]  # XXX: we differ from Rust pest here
    assert err.negatives == []
    assert err.pos == 0


def test_choice_a_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_a_progress", "a")

    err = exec_info.value
    assert err.positives == ["a"]
    assert err.negatives == []
    assert err.pos == 1


def test_choice_b_progress(parser: Parser) -> None:
    with pytest.raises(PestParsingError) as exec_info:
        parser.parse("choices_b_progress", "b")

    err = exec_info.value
    assert err.positives == ["b"]
    assert err.negatives == []
    assert err.pos == 1


# TODO: finish me

# def test_nested(parser: Parser) -> None:
#     with pytest.raises(PestParsingError) as exec_info:
#         parser.parse("level1", "x")

#     err = exec_info.value
#     assert err.positives == ["a", "b", "c"]
#     assert err.negatives == []
#     assert err.pos == 0
