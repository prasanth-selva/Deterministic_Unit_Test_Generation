from targets.fibonacci import fibonacci


def test_fibonacci_zero():
    assert fibonacci(0) == 0


def test_fibonacci_one():
    assert fibonacci(1) == 1


def test_fibonacci_two():
    assert fibonacci(2) == 1


def test_fibonacci_small():
    assert fibonacci(5) == 5


def test_fibonacci_medium():
    assert fibonacci(10) == 55


def test_fibonacci_large():
    assert fibonacci(30) == 832040


def test_fibonacci_with_existing_memo():
    memo = {0: 0, 1: 1, 2: 1}
    assert fibonacci(2, memo) == 1


def test_fibonacci_memo_is_populated():
    memo = {}
    fibonacci(6, memo)
    assert 6 in memo
    assert memo[6] == 8


def test_fibonacci_none_memo_initializes():
    assert fibonacci(4, None) == 3


def test_fibonacci_sequence():
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert [fibonacci(i) for i in range(10)] == expected
