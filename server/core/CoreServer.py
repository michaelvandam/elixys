"""CoreServer

The main executable for the Python service that communicates with the PLC"""

# Imports
import threading
import time
import rpyc
from rpyc.utils.server import ThreadedServer
from SequenceManager import SequenceManager
from SequenceValidationThread import SequenceValidationThread
from CoreServerThread import CoreServerThread
import sys
sys.path.append("/opt/elixys/database")
sys.path.append("/opt/elixys/hardware")
sys.path.append("/opt/elixys/cli")
sys.path.append("/opt/elixys/core/unitoperations")
from DBComm import *
from HardwareComm import HardwareComm
from SystemModel import SystemModel
import Utilities
import json
import Sequences
import UnitOperation
import BaseCLI
from UnitOperationsWrapper import UnitOperationsWrapper
import os
from daemon import daemon
import signal

# Suppress rpyc warning messages
import logging
logging.basicConfig(level=logging.ERROR)

# Initialize global variables
gDatabase = None
gSequenceManager = None
gHardwareComm = None
gSystemModel = None
gUnitOperationsWrapper = None
gRunUsername = ""
gRunSequence = None

# Core server service
class CoreServerService(rpyc.Service):
    def on_connect(self):
        """Invoked when a client connects"""
        global gDatabase
        gDatabase.SystemLog(LOG_INFO, "System", "CoreServerService.connect()")
        # Allow pickling on this connection for proper data transfer
        self._conn._config["allow_pickle"] = True
 
    def on_disconnect(self):
        """Invoked when a client disconnects"""
        global gDatabase
        gDatabase.SystemLog(LOG_INFO, "System", "CoreServerService.disconnect()")

    def exposed_GetServerState(self, sUsername):
        """Returns the state of the server"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.GetServerState()")

        # Get the server state
        pServerState = gSystemModel.GetStateObject()

        # Format the run state
        pServerState["runstate"] = {"type":"runstate"}
        if (gRunSequence != None) and gRunSequence.running:
            pServerState["runstate"]["status"] = ""
            pServerState["runstate"]["prompt"] = {"type":"promptstate",
                "show":False}
            pServerState["runstate"]["timerbuttons"] = []
            pServerState["runstate"]["unitoperationbuttons"] = []
            pUnitOperation = gSystemModel.GetUnitOperation()
            if pUnitOperation != None:
                pServerState["runstate"]["status"] = pUnitOperation.status
                sTimerStatus = pUnitOperation.getTimerStatus()
                if (sTimerStatus == "Running") or (sTimerStatus == "Paused"):
                    if sTimerStatus == "Running":
                        pServerState["runstate"]["timerbuttons"].append({"type":"button",
                            "text":"Pause",
                            "id":"PAUSE"})
                    else:
                        pServerState["runstate"]["timerbuttons"].append({"type":"button",
                            "text":"Continue",
                            "id":"CONTINUE"})
                    pServerState["runstate"]["timerbuttons"].append({"type":"button",
                        "text":"Stop",
                        "id":"STOP"})
                if pUnitOperation.waitingForUserInput:
                    pServerState["runstate"]["unitoperationbuttons"].append({"type":"button",
                            "text":"OK",
                            "id":"USERINPUT"})
            pServerState["runstate"]["username"] = gRunUsername
            pServerState["runstate"]["sequenceid"] = gRunSequence.sequenceID
            pServerState["runstate"]["componentid"] = gRunSequence.componentID
        else:
            gRunSequence = None
            gRunUsername = ""
            pServerState["runstate"]["status"] = "Idle"
            pServerState["runstate"]["prompt"] = {"type":"promptstate",
                "show":False}
            pServerState["runstate"]["username"] = ""
            pServerState["runstate"]["sequenceid"] = 0
            pServerState["runstate"]["componentid"] = 0
            pServerState["runstate"]["timerbuttons"] = []
            pServerState["runstate"]["unitoperationbuttons"] = []

        # Unlock the model and return the server state as a JSON string
        return json.dumps(pServerState)

    def exposed_RunSequence(self, sUsername, nSequenceID):
        """Loads a sequence from the database and runs it"""
        global gDatabase
        global gSystemModel
        global gSequenceManager
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.RunSequence(" + str(nSequenceID) + ")")

        # Make sure we aren't already running a sequence
        if gRunSequence != None:
          if gRunSequence.running:
            gDatabase.SystemLog(LOG_WARNING, sUsername, "A sequence is already running, cannot run another")
            return False
        # Create and start the sequence
        gRunSequence = Sequences.Sequence(sUsername, nSequenceID, gSequenceManager, gSystemModel)
        gRunSequence.setDaemon(True)
        gRunSequence.start()
        gRunUsername = sUsername
        return True

    def exposed_RunSequenceFromComponent(self, sUsername, nSequenceID, nComponentID):
        """Loads a sequence from the database and runs it from the specified component"""
        global gDatabase
        global gSystemModel
        global gSequenceManager
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.RunSequenceFromComponent(" + str(nSequenceID) + ", " + str(nComponentID) + ")")

        # Make sure we aren't already running a sequence
        if gRunSequence != None:
          if gRunSequence.running:
            gDatabase.SystemLog(LOG_WARNING, sUsername, "A sequence is already running, cannot run another")
            return False

        # Create and start the sequence
        gRunSequence = Sequences.Sequence(sUsername, nSequenceID, gSequenceManager, gSystemModel)
        gRunSequence.setDaemon(True)
        gRunSequence.setStartComponent(nComponentID)
        gRunSequence.start()
        gRunUsername = sUsername
        return True

    def exposed_PauseSequence(self, sUsername):
        """Causes the system to pause after the current unit operation is complete"""
        global gDatabase
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.Pause()")
        return False

    def exposed_ContinueSequence(self, sUsername):
        """Continues a paused run"""
        global gDatabase
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.Continue()")
        return False

    def exposed_AbortSequence(self, sUsername):
        """Quickly turns off the heaters and terminates the run, leaving the system in its current state"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.AbortSequence()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "No sequence running, cannot abort")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "Not the user running the sequence, cannot abort")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.SystemLog(LOG_WARNING, sUsername, "No unit operation, cannot abort")
            return False

        # Deliver the abort signal to the current unit operation
        pUnitOperation.setAbort()
        return True

    def exposed_PauseTimer(self, sUsername):
        """Pauses the timer if the unit operation has one running"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.PauseTimer()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "No sequence running, cannot pause timer")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "Not the user running the sequence, cannot pause timer")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.SystemLog(LOG_WARNING, sUsername, "No unit operation, cannot pause timer")
            return False

        # Deliver the pause timer signal to the current unit operation
        pUnitOperation.pauseTimer()
        return True

    def exposed_ContinueTimer(self, sUsername):
        """Continues the timer if the unit operation has one paused"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.ContinueTimer()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "No sequence running, cannot continue timer")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "Not the user running the sequence, cannot continue timer")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.SystemLog(LOG_WARNING, sUsername, "No unit operation, cannot continue timer")
            return False

        # Deliver the continue timer signal to the current unit operation
        pUnitOperation.continueTimer()
        return True

    def exposed_StopTimer(self, sUsername):
        """Cuts the timer short if the unit operation has one running"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.StopTimer()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "No sequence running, cannot stop timer")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "Not the user running the sequence, cannot stop timer")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.SystemLog(Log_WARNING, sUsername, "No unit operation, cannot stop timer")
            return False

        # Deliver the stop timer signal to the current unit operation
        pUnitOperation.stopTimer()
        return True

    def exposed_DeliverUserInput(self, sUsername):
        """Delivers user input to the current unit operation for the CLI"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.DeliverUserInput()")

        # Perform additional check if the user is not the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "No sequence running, cannot deliver user input")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.SystemLog(LOG_WARNING, sUsername, "Not the user running the sequence, cannot deliver user input")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.SystemLog(LOG_WARNING, sUsername, "No unit operation, cannot deliver user input")
            return False

        # Deliver the user input to the current unit operation
        pUnitOperation.deliverUserInput()
        return True
 
    def exposed_CLIExecuteCommand(self, sUsername, sCommand):
        """Executes a command for the CLI"""
        global gDatabase
        global gHardwareComm
        global gSystemModel
        global gUnitOperationsWrapper
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLIExecuteCommand(" + sCommand + ")")

        # Execute the command
        try:
            return BaseCLI.ExecuteCommandImpl(sCommand, gUnitOperationsWrapper, gSystemModel, gHardwareComm)
        except Exception as ex:
            return "Failed to execute command: " + str(ex)

    def exposed_CLISendCommand(self, sUsername, sCommand):
        """Sends a command for the CLI"""
        global gDatabase
        global gHardwareComm
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLISendCommand(" + sCommand + ")")

        # Send the raw command
        try:
            BaseCLI.SendCommandImpl(sCommand, gHardwareComm)
            return ""
        except Exception as ex:
            return "Failed to send command: " + str(ex)

    def exposed_CLIGetState(self, sUsername):
        """Gets the state for the CLI"""
        global gDatabase
        global gSystemModel
        gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLIGetState()")

        # Return the system state
        try:
            return BaseCLI.GetStateImpl(gSystemModel)
        except Exception as ex:
            return "Failed to get system state: " + str(ex)

# Core server daemon exit function
gCoreServerDaemon = None
def OnExit(pCoreServerDaemon, signal, func=None):
    if gCoreServerDaemon != None:
        gCoreServerDaemon.bTerminate = True

# Core server daemon
class CoreServerDaemon(daemon):
    def __init__(self, sPidFile):
        """Initializes the core server daemon"""
        global gCoreServerDaemon
        daemon.__init__(self, sPidFile, "/opt/elixys/logs/CoreServer.log")
        self.bTerminate = False
        gCoreServerDaemon = self

    def run(self):
        """Runs the core server daemon"""
        global gDatabase
        global gSequenceManager
        global gHardwareComm
        global gSystemModel
        global gUnitOperationsWrapper
        global gCoreServerDaemon
        while not self.bTerminate:
            try:
                # Create the database and sequence manager
                gDatabase = DBComm()
                gDatabase.Connect()
                gDatabase.SystemLog(LOG_INFO, "System", "CoreServer starting")
                gSequenceManager = SequenceManager(gDatabase)

                # Create the hardware layer and system model
                gHardwareComm = HardwareComm()
                gHardwareComm.StartUp()
                gSystemModel = SystemModel(gHardwareComm, gDatabase)
                gSystemModel.StartUp()

                # Create the unit operations wrapper
                gUnitOperationsWrapper = UnitOperationsWrapper(gSystemModel)

                # Create the core server
                pCoreServer = ThreadedServer(CoreServerService, port = 18862)
    
                # Start the core server thread
                pCoreServerThread = CoreServerThread()
                pCoreServerThread.SetParameters(pCoreServer)
                pCoreServerThread.setDaemon(True)
                pCoreServerThread.start()

                # Start the background sequence validation thread
                pSequenceValidationThread = SequenceValidationThread()
                pSequenceValidationThread.setDaemon(True)
                pSequenceValidationThread.start()

                # Install the kill signal handler
                signal.signal(signal.SIGTERM, OnExit)
                gDatabase.SystemLog(LOG_INFO, "System", "CoreServer started")

                # Run until we get the signal to stop
                while not self.bTerminate:
                    gSystemModel.CheckForError()
                    pCoreServerThread.CheckForError()
                    try:
                        pSequenceValidationThread.CheckForError()
                    except Exception as ex:
                        gDatabase.SystemLog(LOG_INFO, "System", "Sequence validation thread failed, restarting (" + str(ex) + ")")
                    time.sleep(0.25)
                gDatabase.SystemLog(LOG_INFO, "System", "CoreServer received quit signal")
            except Exception as ex:
                # Log the error
                gDatabase.SystemLog(LOG_ERROR, "System", "CoreServer failed: " + str(ex))
            finally:
                pSequenceValidationThread.Terminate()
                pCoreServerThread.Terminate()
                gDatabase.SystemLog(LOG_INFO, "System", "CoreServer stopped")

            # Sleep for a second before we respawn
            if not self.bTerminate:
                time.sleep(1)
        gCoreServerDaemon = None

# Main function
if __name__ == "__main__":
    if len(sys.argv) == 3:
        pDaemon = CoreServerDaemon(sys.argv[2])
        if 'start' == sys.argv[1]:
            pDaemon.start()
        elif 'stop' == sys.argv[1]:
            pDaemon.stop()
        elif 'restart' == sys.argv[1]:
            pDaemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart pidfile" % sys.argv[0]
        sys.exit(2)

