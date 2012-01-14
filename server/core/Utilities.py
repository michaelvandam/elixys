""" Utilities.py

Utility functions for CLI """

# Imports
import select
import sys
import platform
import threading
import time

# Determine which OS we are running on
if "Windows" in platform.platform():
    gPlatform = "Windows"
    import msvcrt
else:
    gPlatform = "Linux"

# Default lock timeout in seconds
LOCK_TIMEOUT = 3.0

def CheckForQuit():
    """Check if the user pressed 'q' to quit"""
    if gPlatform == "Windows":
        # Check if keyboard input is available
        if msvcrt.kbhit():
            # Check for 'q'
            return msvcrt.getch() == "q"
    else:
        # Use select to read standard in
        pRead, pWrite, pError = select.select([sys.stdin],[],[],0.0001)
        for pReadable in pRead:
            if pReadable == sys.stdin:
                return sys.stdin.read(1) == "q"
            
    # No keyboard input
    return False

def CreateTimedLock():
    """Create a timed lock"""
    # Create a lock and condition used to wait on the lock
    pTimedLock = {}
    pTimedLock["lock"] = threading.Lock()
    pTimedLock["condition"] = threading.Condition(threading.Lock())
    return pTimedLock

def AcquireLock(pTimedLock, fTimeout = 0):
    """Acquire the lock or timeout"""
    # Acquire the lock or wait until it becomes available
    if fTimeout == 0:
        fTimeout = LOCK_TIMEOUT
    with pTimedLock["condition"]:
        nCurrentTime = nStartTime = time.time()
        while nCurrentTime < (nStartTime + fTimeout):
            if pTimedLock["lock"].acquire(False):
                return
            else:
                pTimedLock["condition"].wait(fTimeout - nCurrentTime + nStartTime)
                nCurrentTime = time.time()
    raise Exception("Timed out acquiring lock")

def ReleaseLock(pTimedLock):
    """Releases the lock"""
    # Release the lock and notify any waiting threads
    pTimedLock["lock"].release()
    if pTimedLock["condition"].acquire(False):
        pTimedLock["condition"].notify()
        pTimedLock["condition"].release()

