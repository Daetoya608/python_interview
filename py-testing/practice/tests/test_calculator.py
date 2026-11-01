import pytest

from study_app.calculator import add, divide, is_positive, multiply, subtract

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "a,b,expected", [(2, 3, 5), (-2, 3, 1), (0, 0, 0)], ids=["positive", "mixed", "zeros"]
)
def test_add(a, b, expected):
    assert add(a, b) == expected


def test_subtract_negative_result():
    assert subtract(2, 5) == -3


@pytest.mark.parametrize("a,b,expected", [(2, 3, 6), (9, 0, 0), (-2, 3, -6)])
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [(9, 3, 3), (-9, 3, -3), (0, 2, 0)])
def test_divide(a, b, expected):
    assert divide(a, b) == expected


def test_divide_fraction():
    assert divide(1, 3) == pytest.approx(0.3333333333)


def test_divide_by_zero():
    with pytest.raises(ValueError, match="denominator must not be zero"):
        divide(10, 0)


@pytest.mark.parametrize("value,expected", [(1, True), (0, False), (-1, False)])
def test_is_positive(value, expected):
    assert is_positive(value) is expected
