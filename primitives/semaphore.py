# primitives/semaphore.py
import threading

class Semaphore:
    def __init__(self, count):
        self.sem = threading.Semaphore(count)

    def wait(self):
        self.sem.acquire()

    def signal(self):
        self.sem.release()
