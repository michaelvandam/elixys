""" MoveReactorLinearThread.py

Reactor thread that adjusts the linear position over time"""

### Imports
import threading
import time

class MoveReactorLinearThread(threading.Thread):
    def SetParameters(self, pHardwareComm, nReactor, nStartZ, nTargetZ):
        """Sets the reactor linear movement thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nReactor = nReactor
        self.__nStartZ = nStartZ
        self.__nTargetZ = nTargetZ
        
    def run(self):
        """Thread entry point"""
        # Calculate the step sizes
        z = self.__nStartZ
        nStepZ = (self.__nTargetZ - self.__nStartZ) / 10
        
        # Position adjust loop
        for nCount in range(1, 11):
            # Sleep
            time.sleep(0.1)
            
            # Update the position
            z += nStepZ
            if z < 0:
                z = 0
            self.__pHardwareComm.FakePLC_SetReactorLinearActualPosition(self.__nReactor, z)

        # Set the position to the target
        self.__pHardwareComm.FakePLC_SetReactorLinearActualPosition(self.__nReactor, self.__nTargetZ)
        
        # Sleep an additional second to allow everything to settle
        time.sleep(1)
