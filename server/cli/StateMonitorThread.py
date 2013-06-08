""" StateMonitorThread.py

State monitor thread that runs the server"""

### Imports
import threading
import logging 
log = logging.getLogger("elixys.core")

class StateMonitorThread(threading.Thread):
    def SetParameters(self, pServer):
        """Sets the state monitor thread parameters"""
        self.__pServer = pServer
        
    # Thread function
    def run(self):
        """Thread entry point"""
        log.debug("Running StateMonitorThread")
        # Start the server
        self.__pServer.start()
