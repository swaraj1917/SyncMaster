# problems/producer_consumer.py

import threading
import time
import random
from primitives.mutex import Mutex
from primitives.semaphore import Semaphore
from utils.control import SimulationControl

# Declare global shared objects
buffer = []
empty_slots = None
full_slots = None
mutex = None


def producer(producer_id, items_to_produce):
    global buffer, empty_slots, full_slots, mutex

    for i in range(items_to_produce):
        if SimulationControl.checkpoint():
            return
        item = f"Item-{producer_id}-{i}"
        time.sleep(random.uniform(0.2, 0.5))

        empty_slots.wait()
        if SimulationControl.checkpoint():
            empty_slots.signal()
            return
        mutex.acquire()
        buffer.append(item)
        print(f"Producer {producer_id} produced: {item}")
        mutex.release()
        full_slots.signal()


def consumer(consumer_id, items_to_consume):
    global buffer, empty_slots, full_slots, mutex

    for i in range(items_to_consume):
        if SimulationControl.checkpoint():
            return
        full_slots.wait()
        if SimulationControl.checkpoint():
            full_slots.signal()
            return
        mutex.acquire()
        item = buffer.pop(0)
        print(f"Consumer {consumer_id} consumed: {item}")
        mutex.release()
        empty_slots.signal()
        time.sleep(random.uniform(0.2, 0.5))


def run_simulation(buffer_size, num_producers, num_consumers, items_per_producer):
    global buffer, empty_slots, full_slots, mutex

    buffer = []
    empty_slots = Semaphore(buffer_size)
    full_slots = Semaphore(0)
    mutex = Mutex()

    total_items = num_producers * items_per_producer
    base_items_per_consumer = total_items // num_consumers
    remaining = total_items % num_consumers

    producers = [
        threading.Thread(target=producer, args=(i, items_per_producer),
                         name=f"Producer-{i}")
        for i in range(num_producers)
    ]

    consumers = []
    for i in range(num_consumers):
        items = base_items_per_consumer + (1 if i < remaining else 0)
        consumers.append(
            threading.Thread(target=consumer, args=(i, items),
                             name=f"Consumer-{i}")
        )

    for t in producers + consumers:
        t.start()
    for t in producers + consumers:
        t.join()