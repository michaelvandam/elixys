""" Utilities.py

Utility functions for CLI """

# Imports
import select
import sys
import platform

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

