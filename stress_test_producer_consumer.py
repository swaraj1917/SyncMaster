# stress_test_producer_consumer.py

from primitives.mutex import Mutex
from primitives.semaphore import Semaphore
import threading
import time
import random

BUFFER_SIZE = 10
buffer = []
mutex = Mutex()
empty = Semaphore(BUFFER_SIZE)
full = Semaphore(0)


def producer(pid):
    for i in range(10):
        time.sleep(random.uniform(0.01, 0.1))
        empty.wait()
        mutex.acquire()
        buffer.append((pid, i))
        mutex.release()
        full.signal()


def consumer(cid):
    for i in range(10):
        full.wait()
        mutex.acquire()
        buffer.pop(0)
        mutex.release()
        empty.signal()
        time.sleep(random.uniform(0.01, 0.1))


def run_stress_test():
    producers = [threading.Thread(target=producer, args=(i,)) for i in range(10)]
    consumers = [threading.Thread(target=consumer, args=(i,)) for i in range(10)]

    for t in producers + consumers:
        t.start()
    for t in producers + consumers:
        t.join()

    print("Stress test complete.")


if __name__ == "__main__":
    run_stress_test()