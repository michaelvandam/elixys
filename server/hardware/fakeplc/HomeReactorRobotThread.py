""" HomeReactorRobotThread.py

Reactor thread that adjusts the linear position over time"""

### Imports
import threading
import time

class HomeReactorRobotThread(threading.Thread):
    def SetParameters(self, pHardwareComm, nReactor, nStartY):
        """Sets the reactor linear movement thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nReactor = nReactor
        self.__nStartY = nStartY
        
    def run(self):
        """Thread entry point"""
        # Calculate the step sizes
        y = self.__nStartY
        nStep = -300

        # Start homing the robots
        self.__pHardwareComm.FakePLC_HomeReactorRobot(self.__nReactor)
        self.__pHardwareComm.FakePLC_SetReactorLinearSetPosition(self.__nReactor, 0)
        
        # Position adjust loop
        bContinue = True
        while bContinue:
            # Sleep
            time.sleep(0.1)
            
            # Update the position
            y += nStep
            if y < 0:
                y = 0
                bContinue = False
            self.__pHardwareComm.FakePLC_SetReactorLinearSetPosition(self.__nReactor, y)

        # Sleep an additional second to allow everything to settle
        time.sleep(1)

        # Enable the robots
        self.__pHardwareComm.FakePLC_EnableReactorRobot(self.__nReactor)

