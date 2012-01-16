""" CoreServerThread.py

Core server thread spawned by CoreServer """

### Imports
import threading

class CoreServerThread(threading.Thread):
    def __init__(self):
        """Initialize"""
        threading.Thread.__init__(self)
        self.__bTerminate = False
        self.__sError = ""
        self.__pCoreServer = None

    def SetParameters(self, pCoreServer):
        """Sets the core server thread parameters"""
        self.__pCoreServer = pCoreServer

    def Terminate(self):
        """Flags the thread to terminate"""
        self.__bTerminate = True
        self.__pCoreServer.close()

    # Checks if an error has been encountered
    def CheckForError(self):
        if not self.__bTerminate:
            if self.__sError != "":
                raise Exception(self.__sError)
            if not self.is_alive():
                raise Exception("Core server thread died expectedly")

    # Thread function
    def run(self):
        """Thread entry point"""
        try:
            # Start the server
            self.__pCoreServer.start()
        except Exception as ex:
            self.__sError = str(ex)

