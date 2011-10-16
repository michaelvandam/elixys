"""CoreServer

The main executable for the Python service that communicates with the PLC"""

# Imports
import threading
import time
from rpyc.utils.server import ThreadedServer
from SequenceManager import SequenceManager
from SequenceValidationThread import SequenceValidationThread
import CoreServerService
from CoreServerThread import CoreServerThread
import sys
sys.path.append("../database/")
from DBComm import DBComm
import Utilities

# Global variables user by CoreServerService
gDatabase = DBComm()
gSequenceManager = SequenceManager(gDatabase)

# Main function
if __name__ == "__main__":
    try:
        # Connect to the database
        gDatabase.Connect()
        gDatabase.Log("System", "CoreServer starting")

        # Create the core server
        pCoreServer = ThreadedServer(CoreServerService.CoreServerService, port = 18862)
    
        # Start the core server thread
        pCoreServerThread = CoreServerThread()
        pCoreServerThread.SetParameters(pCoreServer)
        pCoreServerThread.setDaemon(True)
        pCoreServerThread.start()

        # Start the background sequence validation thread
        pSequenceValidationThread = SequenceValidationThread()
        pSequenceValidationThreadEvent = threading.Event()
        pSequenceValidationThread.SetParameters(pSequenceValidationThreadEvent)
        pSequenceValidationThread.setDaemon(True)
        pSequenceValidationThread.start()

        # Run the server until the user presses 'q' to quit
        gDatabase.Log("System", "CoreServer started")
        pUtilities = Utilities.Utilities()
        while not pUtilities.CheckForQuit():
            time.sleep(0.25)

        # Stop the background thread but not the server or it will crash
        gDatabase.Log("System", "CoreServer received quit signal")
        pSequenceValidationThreadEvent.set()
        pSequenceValidationThread.join()
        gDatabase.Log("System", "CoreServer stopped")
    except Exception as ex:
        # Log the error
        gDatabase.Log("System", "CoreServer encountered an error: " + str(ex))

