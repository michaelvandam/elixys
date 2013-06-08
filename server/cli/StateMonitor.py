""" StateMonitor.py

Elixys state monitoring """

# Imports
import time
import rpyc
from rpyc.utils.server import ThreadedServer
import StateMonitorThread
from datetime import datetime
import sys
sys.path.append("/opt/elixys/core/")
import Utilities
import logging

log = logging.getLogger("elixys.core")

# The console package we import depends on the OS
gConsole = None
if sys.platform == "win32":
    try:
        import WConio
        gOS = "Windows"
    except ImportError:
        raise Exception("You must install WConio on Windows")
elif sys.platform == "linux2":
    try:
        import curses
        gOS = "Linux"
    except ImportError:
        raise Exception("You must install curses on Linux")
else:
    raise Exception("Unrecognized platform")

def ClearScreen():
    # Clears the screen and moves the cursor to the upper left corner
    if gOS == "Windows":
        WConio.clrscr()
    elif gOS == "Linux":
        gConsole.erase()
        gConsole.move(0, 0)

def Print(sText):
    # Display the text at the current cursor position
    if gOS == "Windows":
        print sText
    elif gOS == "Linux":
        bScreenToSmall = False
        try:
            gConsole.addstr(sText + "\n")
            gConsole.refresh()
        except Exception,e:
            # Check for terminal too small error
            bScreenToSmall = (str(e) == "addstr() returned ERR")

        # Try to notify the user if the window is too small
        if bScreenToSmall:
            try:
                ClearScreen()
                gConsole.addstr("Terminal window too small to display state\n")
                gConsole.refresh()
            except Exception,e:
                # Ignore any further errors
                pass

# State monitoring service
class StateMonitorService(rpyc.Service):
    def on_connect(self):
        # Clear the screen and notify the user that the client has connected
        ClearScreen()
        Print("Elixys state monitoring system")
        Print("Client connected")
        log.debug("StateMonitorService Connected")

    def on_disconnect(self):
        # Clear the screen and notify the user that the client has disconnected
        ClearScreen()
        Print("Elixys state monitoring system")
        Print("Server disconnected, waiting for another connection (press 'q' to quit)...")
        log.debug("StateMonitorService Disconnected")
 
    def exposed_UpdateState(self, sState):
        # Clear the screen and print the state
        ClearScreen()
        Print(sState)
        Print("Updated at " + time.strftime("%H:%M:%S", time.localtime()))
        log.debug("Update State")

# Main function
if __name__ == "__main__":
    # Notify the user that we are starting
    print "Elixys state monitoring system"
    print "Starting..."

    # Initialize the console on Linux
    if gOS == "Linux":
        gConsole = curses.initscr()

    # Create the RPC server and error handler
    pServer = ThreadedServer(StateMonitorService, port = 18861, logger = log)
    
    # Start the RPC server thread
    pStateMonitorThread = StateMonitorThread.StateMonitorThread()
    pStateMonitorThread.SetParameters(pServer)
    pStateMonitorThread.start()

    # Clear the screen and notify the user that we are waiting for the CLI to connect
    ClearScreen()
    Print("Elixys state monitoring system")
    Print("Waiting for the server to connect (press 'q' to quit)...")
    
    # Run the server until the user presses 'q' to quit
    while not Utilities.CheckForQuit():
        time.sleep(0.25)

    # Stop the RPC server
    pServer.close()
    pStateMonitorThread.join()

    # Clean up the console on Linux
    if gOS == "Linux":
        gConsole = curses.endwin()

    # Say goodbye
    print "Complete"

