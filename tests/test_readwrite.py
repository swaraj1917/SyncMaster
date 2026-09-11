import unittest
import threading
from primitives.semaphore import Semaphore
from primitives.mutex import Mutex
import time

class TestReaderWriter(unittest.TestCase):
    def test_read_write_sequence(self):
        read_count = [0]
        read_count_mutex = Mutex()
        resource_access = Semaphore(1)
        log = []

        def reader():
            read_count_mutex.acquire()
            read_count[0] += 1
            if read_count[0] == 1:
                resource_access.wait()
            read_count_mutex.release()

            log.append("R")

            read_count_mutex.acquire()
            read_count[0] -= 1
            if read_count[0] == 0:
                resource_access.signal()
            read_count_mutex.release()

        def writer():
            resource_access.wait()
            log.append("W")
            resource_access.signal()

        threads = []
        for _ in range(2): threads.append(threading.Thread(target=reader))
        for _ in range(1): threads.append(threading.Thread(target=writer))

        for t in threads: t.start()
        for t in threads: t.join()

        self.assertIn("R", log)
        self.assertIn("W", log)

if __name__ == '__main__':
    unittest.main()
