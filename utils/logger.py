# utils/logger.py
import threading

def log(msg):
    print(f"[{threading.current_thread().name}] {msg}")
