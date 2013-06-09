""" PressureRegulatorThread.py

Pressure regulator thread that adjusts the pressure over time"""

### Imports
import threading
import time
import logging

log = logging.getLogger("elixys.plc")

class PressureRegulatorThread(threading.Thread):
    def SetParameters(self, pHardwareComm, nPressureRegulator, nStartPressure, nTargetPressure):
        """Sets the pressure regulator thread parameters"""
        self.__pHardwareComm = pHardwareComm
        self.__nPressureRegulator = nPressureRegulator
        self.__nStartPressure = nStartPressure
        self.__nTargetPressure = nTargetPressure
        log.debug("Starting Pressure Regulator Thread") 
    def run(self):
        """Thread entry point"""
        try:
            log.debug("Running Pressure Regulator Thread")
            # Calculate the step size
            nPressure = self.__nStartPressure
            nStep = (self.__nTargetPressure - self.__nStartPressure) / 10.0
            log.debug("Start Pressure: %f, Step size: %f ,Stop Pressure: %f" % (self.__nStartPressure, nStep, self.__nTargetPressure)) 
            # Pressure adjust loop
            for nCount in range(1, 11):
                # Sleep
                time.sleep(0.1) 
                
                # Update the pressure
                nPressure += nStep
                self.__pHardwareComm.FakePLC_SetPressureRegulatorActualPressure(self.__nPressureRegulator, nPressure)

            # Set the pressure to the final value
            self.__pHardwareComm.FakePLC_SetPressureRegulatorActualPressure(self.__nPressureRegulator, self.__nTargetPressure)
            log.info("Fake Pressure Reg Done")
			
            # Sleep an additional second to allow everything to settle
            time.sleep(1)
        except Exception as ex:
            log.error("Pressure regulator thread failed")
            import traceback;log.error(traceback.format_exc)
            
