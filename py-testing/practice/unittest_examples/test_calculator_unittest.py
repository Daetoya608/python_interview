import unittest

from study_app.calculator import add, divide, is_positive, multiply, subtract


class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.values = [1, 2]

    def test_add(self):
        self.assertEqual(add(*self.values), 3)

    def test_subtract(self):
        self.assertEqual(subtract(2, 5), -3)

    def test_multiply(self):
        self.assertEqual(multiply(-2, 3), -6)

    def test_positive_and_zero(self):
        self.assertTrue(is_positive(1))
        self.assertFalse(is_positive(0))

    def test_divide(self):
        self.assertAlmostEqual(divide(1, 3), 0.3333333333)

    def test_divide_by_zero(self):
        with self.assertRaisesRegex(ValueError, "denominator must not be zero"):
            divide(1, 0)

    def test_multiple_inputs(self):
        for a, b, expected in [(2, 3, 5), (-2, 3, 1), (0, 0, 0)]:
            with self.subTest(a=a, b=b):
                self.assertEqual(add(a, b), expected)


if __name__ == "__main__":
    unittest.main()
