"""Запуск: python demo.py. Никаких сетевых запросов и внешних ресурсов."""

import asyncio

from typed_examples import (
    Address,
    Scores,
    accumulator,
    apply_to_values,
    count_words,
    display_name,
    fetch_label,
    find_name,
    format_address,
    greet,
    label,
    normalize_id,
    numbers_with_total,
    squares,
    stream_labels,
    use_loader,
)


async def async_demo() -> None:
    print("COROUTINE:", await use_loader(5, fetch_label))
    values = [value async for value in stream_labels(3)]
    print("ASYNC GENERATOR:", values)


def main() -> None:
    users: dict[int, str] = {1: "Anna"}
    address: Address = ("localhost", 8000)
    scores: Scores = {"Anna": [4, 5]}
    print("BASIC:", greet("Anna"))
    print("OPTIONAL:", display_name(find_name(users, 1)), display_name(find_name(users, 99)))
    print("UNION:", normalize_id(42), normalize_id(" 42 "))
    print("COLLECTION:", count_words(["python", "types", "python"]))
    print("ALIAS:", format_address(address), scores)
    print("CALLABLE:", apply_to_values([1, 2], label))
    print("GENERATOR:", list(squares(4)))

    generator = numbers_with_total(4)
    while True:
        try:
            print("YIELD:", next(generator))
        except StopIteration as stop:
            print("GENERATOR RETURN:", stop.value)
            break

    running = accumulator()
    try:
        print("SEND:", next(running), running.send(5), running.send(2))
    finally:
        running.close()

    asyncio.run(async_demo())


if __name__ == "__main__":
    main()
