""" StateMonitor.py

Elixys state monitoring """

### Imports
import WConio
import time
import rpyc
from rpyc.utils.server import ThreadedServer
import Utilities
import StateMonitorThread
from datetime import datetime

# Suppress rpyc warning messages
import logging
logging.basicConfig(level=logging.ERROR)

# State monitoring service
class StateMonitorService(rpyc.Service):
    def on_connect(self):
        # Clear the screen and notify the user that the client has connected
        WConio.clrscr()
        print "Elixys state monitoring system"
        print "Client connected"
 
    def on_disconnect(self):
        # Clear the screen and notify the user that the client has disconnected
        WConio.clrscr()
        print "Elixys state monitoring system"
        print "CLI disconnected, waiting for another connection (press 'q' to quit)..."
 
    def exposed_UpdateState(self, sState):
        # Clear the screen and print the state
        WConio.clrscr()
        print sState
        print "State updated at " + time.strftime("%H:%M:%S", time.localtime())

# Main function
if __name__ == "__main__":
    # Notify the user that we are starting
    print "Elixys state monitoring system"
    print "Starting..."

    # Create the RPC server
    pServer = ThreadedServer(StateMonitorService, port = 18861)
    
    # Start the RPC server thread
    pStateMonitorThread = StateMonitorThread.StateMonitorThread()
    pStateMonitorThread.SetParameters(pServer)
    pStateMonitorThread.start()

    # Clear the screen and notify the user that we are waiting for the CLI to connect
    WConio.clrscr()
    print "Elixys state monitoring system"
    print "Waiting for CLI to connect (press 'q' to quit)..."
    
    # Run the server until the user presses 'q' to quit
    pUtilities = Utilities.Utilities()
    while not pUtilities.CheckForQuit():
        time.sleep(0.25)

    # Stop the RPC server
    pServer.close()
    pStateMonitorThread.join()
