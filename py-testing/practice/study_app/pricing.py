from decimal import Decimal
from os import getenv


def price_in_rubles(amount: Decimal) -> Decimal:
    """Курс из конфигурации — зависимость, которую можно подменить в тесте."""
    if amount < 0:
        raise ValueError("amount must not be negative")
    rate = Decimal(getenv("USD_RATE", "90"))
    if rate <= 0:
        raise ValueError("rate must be positive")
    return amount * rate


async def quote(amount: Decimal, fetch_rate) -> Decimal:
    """fetch_rate — переданная async-функция получения курса валюты."""
    if amount < 0:
        raise ValueError("amount must not be negative")
    rate = await fetch_rate("USD")
    if rate <= 0:
        raise ValueError("rate must be positive")
    return amount * rate
