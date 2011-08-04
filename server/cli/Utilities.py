""" Utilities.py

Utility functions for CLI """

### Imports
import select
import sys
import platform
try:
    import msvcrt
except ImportError:
    pass

# Utilities class
class Utilities():
    def __init__(self):
        """Utilities constructor"""
        # We use different techniques to peek at keyboard input depending on the OS
        if "Windows" in platform.platform():
            self.__sPlatform = "Windows"
        else:
            self.__sPlatform = "Linux"
            
    def CheckForQuit(self):
        """Check if the user pressed 'q' to quit"""
        if self.__sPlatform == "Windows":
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
    
