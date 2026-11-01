from decimal import Decimal
import unittest
from unittest.mock import AsyncMock

from study_app.pricing import quote


class TestQuote(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.provider = AsyncMock(return_value=Decimal("100"))

    async def test_quote(self):
        self.assertEqual(await quote(Decimal("2"), self.provider), Decimal("200"))
        self.provider.assert_awaited_once_with("USD")

    async def test_provider_failure(self):
        self.provider.side_effect = TimeoutError("provider timeout")
        with self.assertRaisesRegex(TimeoutError, "provider timeout"):
            await quote(Decimal("2"), self.provider)


if __name__ == "__main__":
    unittest.main()
