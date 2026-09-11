import unittest
import threading
from primitives.mutex import Mutex
from primitives.semaphore import Semaphore

class TestProducerConsumer(unittest.TestCase):
    def test_buffer_consistency(self):
        buffer = []
        buffer_size = 3
        empty = Semaphore(buffer_size)
        full = Semaphore(0)
        mutex = Mutex()
        result = []

        def producer():
            for i in range(3):
                empty.wait()
                mutex.acquire()
                buffer.append(i)
                result.append(f"P{i}")
                mutex.release()
                full.signal()

        def consumer():
            for i in range(3):
                full.wait()
                mutex.acquire()
                buffer.pop(0)
                result.append(f"C{i}")
                mutex.release()
                empty.signal()

        t1 = threading.Thread(target=producer)
        t2 = threading.Thread(target=consumer)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(len(result), 6)

if __name__ == '__main__':
    unittest.main()
