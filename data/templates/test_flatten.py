from targets.flatten import flatten


def test_flatten_empty_list():
    assert flatten([]) == []


def test_flatten_flat_list():
    assert flatten([1, 2, 3]) == [1, 2, 3]


def test_flatten_single_nested():
    assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]


def test_flatten_deeply_nested():
    assert flatten([1, [2, [3, [4]]]]) == [1, 2, 3, 4]


def test_flatten_mixed_types():
    assert flatten([1, [2, "a"], [True]]) == [1, 2, "a", True]


def test_flatten_nested_empty_lists():
    assert flatten([[], [], []]) == []


def test_flatten_single_element():
    assert flatten([42]) == [42]


def test_flatten_preserves_order():
    assert flatten([[3, 1], [4, 1], [5]]) == [3, 1, 4, 1, 5]


def test_flatten_triple_nested():
    assert flatten([[[1, 2]], [[3]]]) == [1, 2, 3]


def test_flatten_string_not_expanded():
    assert flatten(["hello", ["world"]]) == ["hello", "world"]
