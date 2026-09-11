import threading
import time
import random
from primitives.mutex import Mutex
from utils.control import SimulationControl

forks = []
NUM_PHILOSOPHERS = 5
NAIVE_MODE = False   # NEW: when True, all pick left first → deadlock


def philosopher(philosopher_id, eat_count):
    left_index = philosopher_id
    right_index = (philosopher_id + 1) % NUM_PHILOSOPHERS
    left = forks[left_index]
    right = forks[right_index]

    for i in range(eat_count):
        if SimulationControl.checkpoint():
            return
        print(f"Philosopher {philosopher_id} is thinking...")
        time.sleep(random.uniform(0.5, 1.0))

        if SimulationControl.checkpoint():
            return

        if NAIVE_MODE:
            # Everyone picks LEFT first → deadlock possible
            print(f"Philosopher {philosopher_id} tries to pick up fork {left_index} (left)")
            left.acquire()
            print(f"Philosopher {philosopher_id} picked up fork {left_index}")
            time.sleep(0.05)
            print(f"Philosopher {philosopher_id} tries to pick up fork {right_index} (right)")
            right.acquire()
            print(f"Philosopher {philosopher_id} picked up fork {right_index}")
        else:
            # Asymmetric ordering → no deadlock
            if philosopher_id % 2 == 0:
                left.acquire()
                right.acquire()
                print(
                    f"Philosopher {philosopher_id} is eating using forks "
                    f"{left_index} (left) and {right_index} (right)."
                )
            else:
                right.acquire()
                left.acquire()
                print(
                    f"Philosopher {philosopher_id} is eating using forks "
                    f"{right_index} (right) and {left_index} (left)."
                )

        time.sleep(random.uniform(0.5, 1.0))

        left.release()
        right.release()
        print(f"Philosopher {philosopher_id} released forks "
              f"{left_index} and {right_index}.\n")


def run_simulation(num_philosophers, eat_count, naive=False):
    global forks, NUM_PHILOSOPHERS, NAIVE_MODE
    NUM_PHILOSOPHERS = num_philosophers
    NAIVE_MODE = naive
    forks = [Mutex() for _ in range(NUM_PHILOSOPHERS)]

    threads = [
        threading.Thread(target=philosopher, args=(i, eat_count),
                         name=f"Philosopher-{i}")
        for i in range(NUM_PHILOSOPHERS)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()