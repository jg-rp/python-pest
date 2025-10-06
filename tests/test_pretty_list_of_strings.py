from pest.exceptions import join_with_limit


def test_all_items_fit():
    items = ["apple", "banana", "cherry"]
    result = join_with_limit(items, separator=", ", limit=50)
    assert result == "apple, banana, cherry"


def test_normal_truncation():
    items = ["apple", "banana", "cherry", "date"]
    result = join_with_limit(items, separator=", ", limit=25)
    # Only first 2 items fit, suffix added
    assert result == "apple, banana…(+2 more)"


def test_first_item_too_long_suffix_fits():
    items = ["superlongword"] * 5
    result = join_with_limit(items, separator=", ", limit=15)
    # First item + ellipsis would exceed limit, fallback to only suffix
    assert result == "(5 items)"


def test_first_item_too_long_suffix_does_not_fit():
    items = ["superlongword"] * 5
    result = join_with_limit(items, separator=", ", limit=5)
    # Nothing can fit
    assert result == ""


def test_empty_list():
    items = []
    result = join_with_limit(items, separator=", ", limit=10)
    assert result == ""


def test_limit_exact_fit():
    items = ["a", "b", "c"]
    result = join_with_limit(items, separator=",", limit=5)
    # 'a,b,c' exactly fits
    assert result == "a,b,c"


def test_single_item_fits():
    items = ["apple"]
    result = join_with_limit(items, separator=", ", limit=10)
    assert result == "apple"


def test_single_item_truncated_to_suffix():
    items = ["superlongword"]
    result = join_with_limit(items, separator=", ", limit=5)
    assert result == ""


def test_separator_length_matters():
    items = ["a", "b", "c"]
    result = join_with_limit(items, separator="---", limit=9)
    assert result == "a---b---c"


def test_no_truncation_needed_with_custom_separator():
    items = ["a", "b", "c"]
    result = join_with_limit(items, separator="|", limit=10)
    assert result == "a|b|c"
