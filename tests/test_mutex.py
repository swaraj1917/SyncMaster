import unittest
from primitives.mutex import Mutex
import threading

class TestMutex(unittest.TestCase):
    def test_mutex_lock_unlock(self):
        mutex = Mutex()
        result = []

        def task():
            mutex.acquire()
            result.append(1)
            mutex.release()

        threads = [threading.Thread(target=task) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()

        self.assertEqual(len(result), 5)

if __name__ == '__main__':
    unittest.main()
