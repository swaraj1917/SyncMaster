import unittest
from primitives.semaphore import Semaphore
import threading

class TestSemaphore(unittest.TestCase):
    def test_semaphore_limit(self):
        sem = Semaphore(2)
        active_threads = []

        def worker():
            sem.wait()
            active_threads.append(threading.get_ident())
            self.assertLessEqual(len(active_threads), 2)
            active_threads.remove(threading.get_ident())
            sem.signal()

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()

if __name__ == '__main__':
    unittest.main()
