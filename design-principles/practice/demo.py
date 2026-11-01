"""Small ports-and-adapters example with composition and a decorator."""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Order:
    id: int
    total_cents: int


class Orders(Protocol):
    def add(self, order: Order) -> None: ...


class Notifier(Protocol):
    def send(self, message: str) -> None: ...


class OrderService:
    def __init__(self, orders: Orders, notifier: Notifier):
        self.orders = orders
        self.notifier = notifier

    def place(self, order: Order) -> None:
        if order.total_cents <= 0:
            raise ValueError("order total must be positive")
        self.orders.add(order)
        self.notifier.send(f"Order {order.id} placed")


class MemoryOrders:
    def __init__(self):
        self.items: dict[int, Order] = {}

    def add(self, order: Order) -> None:
        if order.id in self.items:
            raise ValueError("duplicate order")
        self.items[order.id] = order


class RecordingNotifier:
    def __init__(self):
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        self.messages.append(message)


class ConsoleNotifier:
    def send(self, message: str) -> None:
        print(message)


class AuditNotifier:
    def __init__(self, inner: Notifier):
        self.inner = inner
        self.attempts = 0

    def send(self, message: str) -> None:
        self.attempts += 1
        self.inner.send(message)


def make_notifier(recording: bool) -> Notifier:
    return RecordingNotifier() if recording else ConsoleNotifier()


def main():
    repository = MemoryOrders()
    recorder = RecordingNotifier()
    audited = AuditNotifier(recorder)
    service = OrderService(repository, audited)
    service.place(Order(1, 1500))
    assert repository.items[1].total_cents == 1500
    assert recorder.messages == ["Order 1 placed"] and audited.attempts == 1
    try:
        service.place(Order(2, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid order accepted")
    assert 2 not in repository.items and audited.attempts == 1
    print("Domain rule, injected adapters, decorator and invalid-order rejection verified.")
    print("Learning example: DB save + notification is not an atomic transaction; use outbox for durability.")


if __name__ == "__main__":
    main()
