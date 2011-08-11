""" MoveReagentRobotThread.py

Reagent robot thread that adjusts the position over time"""

### Imports
import threading
import time

class MoveReagentRobotThread(threading.Thread):
    def SetParameters(self, pHardwareComm, nStartX, nStartZ, nTargetX, nTargetZ):
        """Sets the pressure regulator thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nStartX = nStartX
        self.__nStartZ = nStartZ
        self.__nTargetX = nTargetX
        self.__nTargetZ = nTargetZ
        
    def run(self):
        """Thread entry point"""
        # Calculate the step sizes
        x = self.__nStartX
        z = self.__nStartZ
        nStepX = (self.__nTargetX - self.__nStartX) / 10
        nStepZ = (self.__nTargetZ - self.__nStartZ) / 10
        
        # Position adjust loop
        for nCount in range(1, 11):
            # Sleep
            time.sleep(0.1)
            
            # Update the position
            x += nStepX
            if x < 0:
                x = 0
            z += nStepZ
            if z < 0:
                z = 0
            self.__pHardwareComm.FakePLC_SetReagentRobotPosition(x, z)

        # Set the position to the target
        self.__pHardwareComm.FakePLC_SetReagentRobotPosition(self.__nTargetX, self.__nTargetZ)
        
        # Sleep an additional second to allow everything to settle
        time.sleep(1)
