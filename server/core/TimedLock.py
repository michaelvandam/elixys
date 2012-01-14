""" TimedLock.py

Thread lock that respects a timeout """

# Imports
import select
import sys
import threading
import time

# Default lock timeout in seconds
LOCK_TIMEOUT = 3.0

class TimedLock():
    def __init__(self):
        """Thread lock with timeout constructor"""
        self.pLock = threading.Lock()
        self.pCondition = threading.Condition(threading.Lock())

    def Acquire(self, fTimeout=0):
        """Acquire the lock or timeout"""
        # Acquire the lock or wait until it becomes available
        if fTimeout == 0:
            fTimeout = LOCK_TIMEOUT
        with self.pCondition:
            nCurrentTime = nStartTime = time.time()
            while nCurrentTime < (nStartTime + fTimeout):
                if self.pLock.acquire(False):
                    return
                else:
                    self.pCondition.wait(fTimeout - nCurrentTime + nStartTime)
                    nCurrentTime = time.time()
        raise Exception("Timed out acquiring lock")

    def Release(self):
        """Releases the lock"""
        # Release the lock and notify any waiting threads
        self.pLock.release()
        if self.pCondition.acquire(False):
            self.pCondition.notify()
            self.pCondition.release()

