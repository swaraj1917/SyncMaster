"""
Global pause/stop control for all simulations.
"""

import threading


class SimulationControl:
    """
    Shared control object for pausing and stopping thread simulations.
    """
    pause_gate = threading.Event()   # set = running, cleared = paused
    stop_flag = threading.Event()    # set = stop requested

    @classmethod
    def init(cls):
        """Reset for a fresh run."""
        cls.pause_gate.set()
        cls.stop_flag.clear()

    @classmethod
    def pause(cls):
        cls.pause_gate.clear()

    @classmethod
    def resume(cls):
        cls.pause_gate.set()

    @classmethod
    def stop(cls):
        cls.stop_flag.set()
        cls.pause_gate.set()   # release anyone waiting on pause

    @classmethod
    def checkpoint(cls):
        """
        Call this from any thread. Blocks if paused, returns True if stop requested.
        """
        if cls.stop_flag.is_set():
            return True
        cls.pause_gate.wait()   # blocks while paused
        return cls.stop_flag.is_set()