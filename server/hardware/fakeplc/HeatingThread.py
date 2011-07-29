""" HeatingThread.py

Heating thread that adjusts the reactor temperature over time"""

### Imports
import threading
import time

class HeatingThread(threading.Thread):
    def __init__(self):
        """Heater thread class constructor"""
        super(HeatingThread, self).__init__()
        self.__pStopEvent = threading.Event()        

    def SetParameters(self, pHardwareComm, nReactor, nStartTemperature, nTargetTemperature):
        """Sets the heating thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nReactor = nReactor
        self.__nStartTemperature = nStartTemperature
        self.__nTargetTemperature = nTargetTemperature

    def Stop(self):
        """Stops the running thread"""
        self.__pStopEvent.set()
        
    def run(self):
        """Thread entry point"""
        # Elixys heating rate in degrees Celsius per 100 ms
        fHeatingRate = 0.217
        nTemperature = self.__nStartTemperature
                
        # Heating loop
        while nTemperature < self.__nTargetTemperature:
            # Sleep
            time.sleep(0.1)
            
            # Update the temperature
            nTemperature += fHeatingRate
            self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, nTemperature)
            
            # Check for thread termination
            if self.__pStopEvent.isSet():
                return

        # Set the position to the target
        self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, self.__nTargetTemperature)
        
        # Sleep an additional second to allow everything to settle
        time.sleep(1)
