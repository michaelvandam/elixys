""" MoveReactorVerticalThread.py

Reactor thread that adjusts the vertical position over time"""

### Imports
import threading
import time

class MoveReactorVerticalThread(threading.Thread):
    def SetParameters(self, pHardwareComm, nReactor, bMoveUp):
        """Sets the reactor vertical movement thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nReactor = nReactor
        self.__bMoveUp = bMoveUp
        
    def run(self):
        """Thread entry point"""
        # Start with a pause
        time.sleep(0.1)
            
        # Clear both reactor position sensors
        self.__pHardwareComm.FakePLC_SetReactorVerticalPosition(self.__nReactor, False, False)

        # Pause again
        time.sleep(1)

        # Set the reactor sensors
        self.__pHardwareComm.FakePLC_SetReactorVerticalPosition(self.__nReactor, self.__bMoveUp, not self.__bMoveUp)
            
        # Sleep an additional second to allow everything to settle
        time.sleep(1)
