""" StateMonitorThread.py

State monitor thread that runs the server"""

### Imports
import threading

class StateMonitorThread(threading.Thread):
    def SetParameters(self, pServer):
        """Sets the state monitor thread parameters"""
        self.__pServer = pServer
        
    # Thread function
    def run(self):
        """Thread entry point"""
        # Start the server
        self.__pServer.start()
