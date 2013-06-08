""" StateUpdateThread.py

State update thread class spawned by SystemModel """

### Imports
import threading
import time

import logging
log = logging.getLogger("elixys")

class StateUpdateThread(threading.Thread):
    # Set parameters
    def SetParameters(self, pHardwareComm, pTerminateEvent):
        # Remember the parameters
        self.__pHardwareComm = pHardwareComm
        self.__pTerminateEvent = pTerminateEvent

        # Initialize variables
        self.__sError = ""

    # Returns any error
    def GetError(self):
        return self.__sError

    # Thread function
    def run(self):
        try:
            # State updating loop
            while not self.__pTerminateEvent.is_set():
                # Update the state
                self.__pHardwareComm.UpdateState()
            
                # Sleep
                time.sleep(0.5)
        except Exception as ex:
            # Remember the error
            log.error("Traceback:\r\n%s\r\n" % traceback.format_exc())
            self.__sError = str(ex)

