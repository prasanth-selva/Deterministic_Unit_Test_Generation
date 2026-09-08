import pytest
from targets.stack import Stack


def test_push_increments_size():
    s = Stack()
    s.push(42)
    assert s.size() == 1


def test_push_multiple_increments_size():
    s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.size() == 3


def test_pop_returns_last_pushed():
    s = Stack()
    s.push(10)
    s.push(20)
    assert s.pop() == 20


def test_pop_decrements_size():
    s = Stack()
    s.push(1)
    s.push(2)
    s.pop()
    assert s.size() == 1


def test_pop_empty_raises_index_error():
    s = Stack()
    with pytest.raises(IndexError):
        s.pop()


def test_peek_returns_top_without_removing():
    s = Stack()
    s.push(99)
    assert s.peek() == 99
    assert s.size() == 1


def test_peek_empty_raises_index_error():
    s = Stack()
    with pytest.raises(IndexError):
        s.peek()


def test_is_empty_true_on_new_stack():
    s = Stack()
    assert s.is_empty() is True


def test_is_empty_false_after_push():
    s = Stack()
    s.push(0)
    assert s.is_empty() is False


def test_is_empty_true_after_pop():
    s = Stack()
    s.push(1)
    s.pop()
    assert s.is_empty() is True


def test_size_zero_on_new_stack():
    s = Stack()
    assert s.size() == 0


def test_lifo_order():
    s = Stack()
    for i in range(5):
        s.push(i)
    result = [s.pop() for _ in range(5)]
    assert result == [4, 3, 2, 1, 0]


def test_push_none_value():
    s = Stack()
    s.push(None)
    assert s.peek() is None
