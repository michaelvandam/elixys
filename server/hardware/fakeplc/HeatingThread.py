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

    def SetParameters(self, pHardwareComm, nReactor, nHeater1On, nHeater2On, nHeater3On, nHeater1StartTemperature, nHeater2StartTemperature, nHeater3StartTemperature, 
        nHeater1TargetTemperature, nHeater2TargetTemperature, nHeater3TargetTemperature):
        """Sets the heating thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nReactor = nReactor
        self.__nHeater1On = nHeater1On
        self.__nHeater2On = nHeater2On
        self.__nHeater3On = nHeater3On
        self.__nHeater1StartTemperature = nHeater1StartTemperature
        self.__nHeater2StartTemperature = nHeater2StartTemperature
        self.__nHeater3StartTemperature = nHeater3StartTemperature
        self.__nHeater1TargetTemperature = nHeater1TargetTemperature
        self.__nHeater2TargetTemperature = nHeater2TargetTemperature
        self.__nHeater3TargetTemperature = nHeater3TargetTemperature

    def Stop(self):
        """Stops the running thread"""
        self.__pStopEvent.set()
        
    def run(self):
        """Thread entry point"""
        # Elixys heating rate in degrees Celsius per 100 ms
        fHeatingRate = 0.217
        nHeater1Temperature = self.__nHeater1StartTemperature
        nHeater2Temperature = self.__nHeater2StartTemperature
        nHeater3Temperature = self.__nHeater3StartTemperature
                
        # Heating loop
        bHeating = True
        while bHeating:
            # Check if any heaters are not at the target temperature
            bHeat1 = self.__nHeater1On and (nHeater1Temperature < self.__nHeater1TargetTemperature)
            bHeat2 = self.__nHeater2On and (nHeater2Temperature < self.__nHeater2TargetTemperature)
            bHeat3 = self.__nHeater3On and (nHeater3Temperature < self.__nHeater3TargetTemperature)
            if bHeat1 or bHeat2 or bHeat3:
                # Sleep a bit
                time.sleep(0.1)
            
                # Update the temperatures
                if bHeat1:
                    nHeater1Temperature += fHeatingRate
                    self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, 1, nHeater1Temperature)
                if bHeat2:
                    nHeater2Temperature += fHeatingRate
                    self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, 2, nHeater2Temperature)
                if bHeat3:
                    nHeater3Temperature += fHeatingRate
                    self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, 3, nHeater3Temperature)
            
                # Check for thread termination
                if self.__pStopEvent.isSet():
                    return
            else:
                bHeating = False

        # Set the temperature to the target
        self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, 1, self.__nHeater1TargetTemperature)
        self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, 2, self.__nHeater2TargetTemperature)
        self.__pHardwareComm.FakePLC_SetReactorActualTemperature(self.__nReactor, 3, self.__nHeater3TargetTemperature)
        
        # Sleep an additional second to allow everything to settle
        time.sleep(1)
