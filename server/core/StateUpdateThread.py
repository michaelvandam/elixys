""" StateUpdateThread.py

State update thread class spawned by SystemModel """

### Imports
import threading
import time

class StateUpdateThread(threading.Thread):
    # Set parameters
    def SetParameters(self, pHardwareComm, pTerminateEvent):
        # Remember the parameters
        self.__pHardwareComm = pHardwareComm
        self.__pTerminateEvent = pTerminateEvent

    # Thread function
    def run(self):
        # State updating loop
        while not self.__pTerminateEvent.is_set():
            # Update the state
            self.__pHardwareComm.UpdateState()
            
            # Sleep
            time.sleep(0.5)
