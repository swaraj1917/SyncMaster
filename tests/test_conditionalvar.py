import unittest
from primitives.condition_variable import ConditionVariable
import threading
import time

class TestConditionVariable(unittest.TestCase):
    def test_wait_signal(self):
        cond = ConditionVariable()
        flag = {"ready": False}

        def waiter():
            cond.wait()
            flag["ready"] = True

        t = threading.Thread(target=waiter)
        t.start()
        time.sleep(0.5)
        cond.signal()
        t.join()
        self.assertTrue(flag["ready"])

if __name__ == '__main__':
    unittest.main()
