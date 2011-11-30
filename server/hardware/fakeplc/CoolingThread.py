""" CoolingThread.py

Cooling thread that adjusts the temperature of the reactors over time"""

### Imports
import threading
import time

class CoolingThread(threading.Thread):
    def __init__(self):
        """Heater thread class constructor"""
        super(CoolingThread, self).__init__()
        self.__pStopEvent = threading.Event()        
        
    def SetParameters(self, pHardwareComm, nR1C1StartTemperature, nR1C2StartTemperature, nR1C3StartTemperature, nR2C1StartTemperature, nR2C2StartTemperature, 
        nR2C3StartTemperature, nR3C1StartTemperature, nR3C2StartTemperature, nR3C3StartTemperature):
        """Sets the heating thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nR1C1StartTemperature = nR1C1StartTemperature
        self.__nR1C2StartTemperature = nR1C2StartTemperature
        self.__nR1C3StartTemperature = nR1C3StartTemperature
        self.__nR2C1StartTemperature = nR2C1StartTemperature
        self.__nR2C2StartTemperature = nR2C2StartTemperature
        self.__nR2C3StartTemperature = nR2C3StartTemperature
        self.__nR3C1StartTemperature = nR3C1StartTemperature
        self.__nR3C2StartTemperature = nR3C2StartTemperature
        self.__nR3C3StartTemperature = nR3C3StartTemperature
        
    def Stop(self):
        """Stops the running thread"""
        self.__pStopEvent.set()
        
    def run(self):
        """Thread entry point"""
        # Elixys cooling rate in degrees Celsius per 100 ms
        fCoolingRate = -0.471
        
        # Lowest temperature
        nBottomTemp = 27
        
        # Reactor starting temperatures
        nReactorTemperatures = [self.__nR1C1StartTemperature, self.__nR1C2StartTemperature, self.__nR1C3StartTemperature,
            self.__nR2C1StartTemperature, self.__nR2C2StartTemperature, self.__nR2C3StartTemperature,
            self.__nR3C1StartTemperature, self.__nR3C2StartTemperature, self.__nR3C3StartTemperature]
                
        # Cooling loop
        bCooling = True
        while bCooling:
            # Sleep
            time.sleep(0.1)
            
            # Clear our cooling flag
            bCooling = False
            
            # Update the temperature of each reactor
            for nReactor in range(0, 3):
                # Update the temperature of each collet
                for nHeater in range(0, 3):
                    # Has this reactor fully cooled?
                    if nReactorTemperatures[(nReactor * 3) + nHeater] > nBottomTemp:
                        # No, so set our cooling flag
                        bCooling = True

                        # Adjust the temperature
                        nReactorTemperatures[(nReactor * 3) + nHeater] += fCoolingRate
                    
                        # Update the temperature on the PLC
                        self.__pHardwareComm.FakePLC_SetReactorActualTemperature(nReactor + 1, nHeater + 1, nReactorTemperatures[(nReactor * 3) + nHeater])

            # Check for thread termination
            if self.__pStopEvent.isSet():
                return
                
        # Sleep an additional second to allow everything to settle
        time.sleep(1)
