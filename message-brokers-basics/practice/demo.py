"""An in-process queue demonstrates roles, not broker reliability."""
from queue import Queue
from threading import Thread


def main():
    queue = Queue()
    processed = []

    def consumer():
        while True:
            message = queue.get()
            try:
                if message is None:
                    return
                processed.append(message["id"])
            finally:
                queue.task_done()

    worker = Thread(target=consumer)
    worker.start()
    for number in range(3):
        queue.put({"id": number, "task": "send_email"})
    queue.put(None)
    queue.join()
    worker.join()
    assert processed == [0, 1, 2]
    print("Producer -> in-process queue -> consumer:", processed)


if __name__ == "__main__":
    main()
