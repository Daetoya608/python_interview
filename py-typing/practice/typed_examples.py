"""Примеры аннотаций для Python 3.11+, проверяемые mypy --strict."""

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator, Iterable, Mapping
from typing import TypeAlias

Address: TypeAlias = tuple[str, int]
Scores: TypeAlias = dict[str, list[int]]


def greet(name: str, repeats: int = 1) -> str:
    if repeats < 1:
        raise ValueError("repeats must be positive")
    return " ".join([f"Hello, {name}!"] * repeats)


def find_name(users: Mapping[int, str], user_id: int) -> str | None:
    return users.get(user_id)


def display_name(name: str | None) -> str:
    if name is None:
        return "Anonymous"
    return name.upper()


def normalize_id(value: int | str) -> str:
    if isinstance(value, int):
        return str(value)
    return value.strip()


def count_words(words: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def format_address(address: Address) -> str:
    host, port = address
    return f"{host}:{port}"


def apply_to_values(values: Iterable[int], transform: Callable[[int], str]) -> list[str]:
    return [transform(value) for value in values]


def label(value: int) -> str:
    return f"item-{value}"


def squares(limit: int) -> Generator[int, None, None]:
    for number in range(limit):
        yield number * number


def numbers_with_total(limit: int) -> Generator[int, None, int]:
    total = 0
    for number in range(limit):
        total += number
        yield number
    return total


def accumulator() -> Generator[int, int, None]:
    total = 0
    while True:
        increment = yield total
        total += increment


async def fetch_label(value: int) -> str:
    await asyncio.sleep(0)
    return label(value)


async def use_loader(value: int, loader: Callable[[int], Awaitable[str]]) -> str:
    return await loader(value)


async def stream_labels(limit: int) -> AsyncGenerator[str, None]:
    for number in range(limit):
        yield await fetch_label(number)
