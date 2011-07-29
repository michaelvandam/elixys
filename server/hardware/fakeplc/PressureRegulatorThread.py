""" PressureRegulatorThread.py

Pressure regulator thread that adjusts the pressure over time"""

### Imports
import threading
import time

class PressureRegulatorThread(threading.Thread):
    def SetParameters(self, pHardwareComm, nPressureRegulator, nStartPressure, nTargetPressure):
        """Sets the pressure regulator thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nPressureRegulator = nPressureRegulator
        self.__nStartPressure = nStartPressure
        self.__nTargetPressure = nTargetPressure
        
    def run(self):
        """Thread entry point"""
        # Calculate the step size
        nPressure = self.__nStartPressure
        nStep = (self.__nTargetPressure - self.__nStartPressure) / 10
        
        # Pressure adjust loop
        for nCount in range(1, 11):
            # Sleep
            time.sleep(0.1)
            
            # Update the pressure
            nPressure += nStep
            self.__pHardwareComm.FakePLC_SetPressureRegulatorActualPressure(self.__nPressureRegulator, nPressure)

        # Sleep an additional second to allow everything to settle
        time.sleep(1)
        