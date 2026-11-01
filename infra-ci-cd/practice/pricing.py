def total_cents(price_cents: int, quantity: int) -> int:
    if price_cents < 0 or quantity < 0:
        raise ValueError("price and quantity must be non-negative")
    return price_cents * quantity
