# primitives/condition_variable.py
import threading

class ConditionVariable:
    def __init__(self):
        self.condition = threading.Condition()

    def wait(self):
        with self.condition:
            self.condition.wait()

    def signal(self):
        with self.condition:
            self.condition.notify()
