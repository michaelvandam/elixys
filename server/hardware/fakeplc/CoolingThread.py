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
        
    def SetParameters(self, pHardwareComm, nReactor1StartTemperature, nReactor2StartTemperature, nReactor3StartTemperature):
        """Sets the heating thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nReactor1StartTemperature = nReactor1StartTemperature
        self.__nReactor2StartTemperature = nReactor2StartTemperature
        self.__nReactor3StartTemperature = nReactor3StartTemperature
        
    def Stop(self):
        """Stops the running thread"""
        self.__pStopEvent.set()
        
    def run(self):
        """Thread entry point"""
        # Elixys cooling rate in degrees Celsius per 100 ms
        fCoolingRate1 = -0.471
        fCoolingRate2 = -0.018
        
        # Cutoff temperature above which we use rate 1 and below which we use rate 2
        nTemperatureCutoff = 58
        
        # Lowest temperature
        nBottomTemp = 27
        
        # Reactor starting temperatures
        nReactorTemperatures = [self.__nReactor1StartTemperature, self.__nReactor2StartTemperature, self.__nReactor3StartTemperature]
                
        # Cooling loop
        bCooling = True
        while bCooling:
            # Sleep
            time.sleep(0.1)
            
            # Clear our cooling flag
            bCooling = False
            
            # Update the temperature of each reactor
            for nReactor in range(1, 4):
                # Has this reactor fully cooled?
                if nReactorTemperatures[nReactor - 1] > nBottomTemp:
                    # No, so set our cooling flag
                    bCooling = True

                    # Adjust the temperature
                    if nReactorTemperatures[nReactor - 1] > nTemperatureCutoff:
                        nReactorTemperatures[nReactor - 1] += fCoolingRate1
                    else:
                        nReactorTemperatures[nReactor - 1] += fCoolingRate2
                    
                    # Update the temperature on the PLC
                    self.__pHardwareComm.FakePLC_SetReactorActualTemperature(nReactor, nReactorTemperatures[nReactor - 1])

            # Check for thread termination
            if self.__pStopEvent.isSet():
                return
                
        # Sleep an additional second to allow everything to settle
        time.sleep(1)
