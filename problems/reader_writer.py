# problems/reader_writer.py

import threading
import time
import random
from primitives.mutex import Mutex
from primitives.semaphore import Semaphore
from utils.control import SimulationControl

read_count = 0
read_count_mutex = Mutex()
resource_access = Semaphore(1)


def reader(reader_id, read_times):
    global read_count
    for _ in range(read_times):
        if SimulationControl.checkpoint():
            return
        time.sleep(random.uniform(0.5, 1.0))

        read_count_mutex.acquire()
        read_count += 1
        if read_count == 1:
            resource_access.wait()
        read_count_mutex.release()

        print(f"Reader {reader_id} is reading...")
        time.sleep(random.uniform(0.5, 1.0))
        print(f"Reader {reader_id} finished reading.")

        read_count_mutex.acquire()
        read_count -= 1
        if read_count == 0:
            resource_access.signal()
        read_count_mutex.release()


def writer(writer_id, write_times):
    for _ in range(write_times):
        if SimulationControl.checkpoint():
            return
        time.sleep(random.uniform(0.5, 1.0))

        resource_access.wait()
        print(f"Writer {writer_id} is writing...")
        time.sleep(random.uniform(0.5, 1.0))
        print(f"Writer {writer_id} finished writing.")
        resource_access.signal()


def run_simulation(num_readers, num_writers, read_times, write_times):
    threads = []

    for i in range(num_readers):
        threads.append(threading.Thread(target=reader, args=(i, read_times),
                                        name=f"Reader-{i}"))
    for i in range(num_writers):
        threads.append(threading.Thread(target=writer, args=(i, write_times),
                                        name=f"Writer-{i}"))

    for t in threads:
        t.start()
    for t in threads:
        t.join()