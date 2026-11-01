import unittest
from pricing import total_cents


class PricingTest(unittest.TestCase):
    def test_total_and_empty_order(self):
        self.assertEqual(total_cents(125, 3), 375)
        self.assertEqual(total_cents(125, 0), 0)

    def test_negative_inputs_rejected(self):
        for price, quantity in [(-1, 2), (100, -1)]:
            with self.subTest(price=price, quantity=quantity):
                with self.assertRaises(ValueError):
                    total_cents(price, quantity)
