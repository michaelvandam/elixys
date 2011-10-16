""" CoreServerThread.py

Core server thread spawned by CoreServer """

### Imports
import threading

class CoreServerThread(threading.Thread):
    def SetParameters(self, pCoreServer):
        """Sets the core server thread parameters"""
        self.__pCoreServer = pCoreServer
        
    # Thread function
    def run(self):
        """Thread entry point"""
        # Start the server
        self.__pCoreServer.start()

