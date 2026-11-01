import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from study_app.pricing import quote

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_quote_awaits_provider():
    provider = AsyncMock(return_value=Decimal("100"))
    assert await quote(Decimal("2"), provider) == Decimal("200")
    provider.assert_awaited_once_with("USD")


async def test_negative_amount_does_not_await_provider():
    provider = AsyncMock()
    with pytest.raises(ValueError, match="amount must not be negative"):
        await quote(Decimal("-1"), provider)
    provider.assert_not_awaited()


async def test_provider_failure_propagates():
    provider = AsyncMock(side_effect=TimeoutError("provider timeout"))
    with pytest.raises(TimeoutError, match="provider timeout"):
        await quote(Decimal("2"), provider)


async def test_nonpositive_provider_rate_is_rejected():
    provider = AsyncMock(return_value=Decimal("0"))
    with pytest.raises(ValueError, match="rate must be positive"):
        await quote(Decimal("2"), provider)


async def test_cancellation_reaches_provider_cleanup():
    started = asyncio.Event()
    cleaned_up = asyncio.Event()

    async def provider(currency):
        try:
            started.set()
            await asyncio.Event().wait()
        finally:
            cleaned_up.set()

    task = asyncio.create_task(quote(Decimal("2"), provider))
    try:
        await asyncio.wait_for(started.wait(), timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cleaned_up.is_set()
    finally:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
