""" HomeReagentRobotThread.py

Reagent robot thread that adjusts the position over time"""

### Imports
import threading
import time

class HomeReagentRobotThread(threading.Thread):
    def SetParameters(self, pHardwareComm, nStartX, nStartY):
        """Sets the home reagent robot thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nStartX = nStartX
        self.__nStartY = nStartY
        
    def run(self):
        """Thread entry point"""
        # Calculate the step sizes
        x = self.__nStartX
        y = self.__nStartY
        nStep = -300

        # Start homing the robots
        self.__pHardwareComm.FakePLC_HomeReagentRobotX()
        self.__pHardwareComm.FakePLC_HomeReagentRobotY()
        self.__pHardwareComm.FakePLC_SetReagentRobotSetPosition(0, 0)
        
        # Position adjust loop
        bContinue = True
        while bContinue:
            # Sleep
            time.sleep(0.1)
            
            # Update the position
            x += nStep
            if x < 0:
                x = 0
            y += nStep
            if y < 0:
                y = 0
            self.__pHardwareComm.FakePLC_SetReagentRobotActualPosition(x, y)

            # Check for completion
            if (x == 0) and (y == 0):
                bContinue = False

        # Sleep an additional second to allow everything to settle
        time.sleep(1)

        # Enable the robots
        self.__pHardwareComm.FakePLC_EnableReagentRobotX()
        self.__pHardwareComm.FakePLC_EnableReagentRobotY()

