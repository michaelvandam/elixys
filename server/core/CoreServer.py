"""CoreServer

The main executable for the Python service that communicates with the PLC"""

# Imports
import threading
import time
import rpyc
from rpyc.utils.server import ThreadedServer
from CoreServerThread import CoreServerThread
import sys
sys.path.append("/opt/elixys/database")
sys.path.append("/opt/elixys/hardware")
sys.path.append("/opt/elixys/cli")
sys.path.append("/opt/elixys/core")
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
import logging
import TimedLock
from Messaging import Messaging

# Initialize global variables
gCoreServerLock = None
gServerStateLock = None
gServerState = None
gServerStateTime = 0
gDatabase = None
gHardwareComm = None
gSystemModel = None
gUnitOperationsWrapper = None
gRunUsername = ""
gRunSequence = None
gMessaging = None

# Handler that redirects rpyc error messages to the database
class RpycLogHandler(logging.StreamHandler):
    def emit(self, record):
        """Error message handler"""
        # Format the multiline message into a single line
        global gDatabase
        sMultilineMessage = self.format(record)
        pMultilineMessageComponents = sMultilineMessage.split("\n")
        sLogMessage = "rpyc: " + pMultilineMessageComponents[0]
        nLength = len(pMultilineMessageComponents)
        if len(pMultilineMessageComponents) > 1:
            sLogMessage += " (" + pMultilineMessageComponents[nLength - 1] + ")"

        # Log the message
        if gDatabase != None:
            gDatabase.SystemLog(LOG_WARNING, "System", sLogMessage)
        else:
            print sLogMessage

# Core server service
class CoreServerService(rpyc.Service):
    def exposed_GetServerState(self, sUsername):
        """Returns the state of the server"""
        global gCoreServerLock
        global gServerStateLock
        global gServerState
        global gServerStateTime
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bServerStateLocked = False
        bCoreServerLocked = False
        try:
            # Acquire the server state lock
            gServerStateLock.Acquire(1)
            bServerStateLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.GetServerState()")

            # Update the server state twice per second
            if (gServerState == None) or ((time.time() - gServerStateTime) > 0.5):
                # Acquire the core server lock
                gCoreServerLock.Acquire(1)
                bCoreServerLocked = True

                # Get the server state
                gServerState = gSystemModel.GetStateObject()
                gServerStateTime = time.time()
                if gServerState == None:
                    raise Exception("Failed to get server state")

                # Get the initial run state
                gServerState["runstate"] = InitialRunState()

                # Check if the system is running or idle
                if (gRunSequence != None) and (gRunSequence.initializing or gRunSequence.running):
                    # System is running
                    gServerState["runstate"]["runcomplete"] = gRunSequence.isRunComplete()
                    gServerState["runstate"]["running"] = True
                    gServerState["runstate"]["username"] = gRunUsername
                    nSequenceID, nComponentID = gRunSequence.getIDs()
                    gServerState["runstate"]["sequenceid"] = nSequenceID
                    gServerState["runstate"]["componentid"] = nComponentID
                    pUnitOperation = gSystemModel.GetUnitOperation()
                    if pUnitOperation != None:
                        gServerState["runstate"]["description"] = pUnitOperation.description
                        gServerState["runstate"]["status"] = pUnitOperation.status
                        sTimerStatus = pUnitOperation.getTimerStatus()
                        if (sTimerStatus == "Running"):
                            gServerState["runstate"]["time"] = self.FormatTime(pUnitOperation.getTime())
                            gServerState["runstate"]["timedescription"] = "TIME REMAINING"
                        elif (sTimerStatus == "Overridden"):
                            gServerState["runstate"]["time"] = self.FormatTime(pUnitOperation.getTime())
                            gServerState["runstate"]["timedescription"] = "TIME ELAPSED"
                        elif pUnitOperation.waitingForUserInput:
                            gServerState["runstate"]["waitingforuserinput"] = True
                        if gRunSequence.willRunPause():
                            gServerState["runstate"]["useralert"] = "Run will pause after the current operation."
                        if gRunSequence.getShowAbortPrompt():
                            gServerState["runstate"]["prompt"]["screen"] = "PROMPT_ABORTRUN"
                            gServerState["runstate"]["prompt"]["show"] = True
                            gServerState["runstate"]["prompt"]["title"] = "ABORT RUN"
                            gServerState["runstate"]["prompt"]["text1"] = "Are you sure you want to abort this run?"
                            gServerState["runstate"]["prompt"]["edit1"] = False
                            gServerState["runstate"]["prompt"]["text2"] = ""
                            gServerState["runstate"]["prompt"]["edit2"] = False
                            gServerState["runstate"]["prompt"]["buttons"] = [{"type":"button",
                                "text":"YES",
                                "id":"YES"},
                                {"type":"button",
                                "text":"NO",
                                "id":"NO"}]
                        else:
                            (sSoftError, pOptions) = pUnitOperation.getSoftError()
                            if sSoftError != "":
                                gServerState["runstate"]["prompt"]["screen"] = "PROMPT_SOFTERROR"
                                gServerState["runstate"]["prompt"]["show"] = False
                                gServerState["runstate"]["prompt"]["title"] = "ERROR"
                                gServerState["runstate"]["prompt"]["text1"] = sSoftError
                                gServerState["runstate"]["prompt"]["edit1"] = False
                                gServerState["runstate"]["prompt"]["text2"] = ""
                                gServerState["runstate"]["prompt"]["edit2"] = False
                                gServerState["runstate"]["prompt"]["buttons"] = []
                                for sOption in pOptions:
                                    gServerState["runstate"]["prompt"]["buttons"].append({"type":"button",
                                        "text":sOption,
                                        "id":sOption})
                else:
                    # The system is idle
                    gRunSequence = None
                    gRunUsername = ""
                    gServerState["runstate"]["status"] = "Idle"

            # Update the user-specific parts of the state
            gServerState["runstate"]["unitoperationbutton"] = {"type":"button",
                "text":"",
                "id":""}
            if gRunUsername == sUsername:
                if gServerState["runstate"]["timedescription"] == "TIME REMAINING":
                    gServerState["runstate"]["unitoperationbutton"] = {"type":"button",
                        "text":"OVERRIDE TIMER",
                        "id":"TIMEROVERRIDE"}
                elif gServerState["runstate"]["timedescription"] == "TIME ELAPSED":
                    gServerState["runstate"]["unitoperationbutton"] = {"type":"button",
                        "text":"FINISH UNIT OPERATION",
                        "id":"TIMERCONTINUE"}
                elif gServerState["runstate"]["waitingforuserinput"]:
                    gServerState["runstate"]["unitoperationbutton"] = {"type":"button",
                        "text":"CONTINUE",
                        "id":"USERINPUT"}
                if gServerState["runstate"]["prompt"]["title"] != "":
                    gServerState["runstate"]["prompt"]["show"] = True

            # Format the server state as a JSON string
            pResult = self.SuccessResult(json.dumps(gServerState))
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.GetServerState() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bServerStateLocked:
            gServerStateLock.Release()
        if bCoreServerLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_RunSequence(self, sUsername, nSequenceID):
        """Loads a sequence from the database and runs it"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.RunSequence(" + str(nSequenceID) + ")")

            # Make sure we aren't already running a sequence
            if (gRunSequence != None) and gRunSequence.running:
                # Throw an exception if we aren't the user running the system
                if gRunUsername != sUsername:
                    raise Exception("A sequence is already running, cannot run another")
            else:
                # Create and start the sequence
                gRunSequence = Sequences.Sequence(sUsername, nSequenceID, gSystemModel)
                gRunSequence.setDaemon(True)
                gRunSequence.start()
                gRunUsername = sUsername
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.RunSequence() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_RunSequenceFromComponent(self, sUsername, nSequenceID, nComponentID):
        """Loads a sequence from the database and runs it from the specified component"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.RunSequenceFromComponent(" + str(nSequenceID) + ", " + str(nComponentID) + ")")

            # Make sure we aren't already running a sequence
            if gRunSequence != None:
              if gRunSequence.running:
                raise Exception("A sequence is already running, cannot run another")

            # Create and start the sequence
            gRunSequence = Sequences.Sequence(sUsername, nSequenceID, gSystemModel)
            gRunSequence.setDaemon(True)
            gRunSequence.setStartComponent(nComponentID)
            gRunSequence.start()
            gRunUsername = sUsername
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.RunSequenceFromComponent() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_PauseSequence(self, sUsername):
        """Causes the system to pause after the current unit operation is complete"""
        global gCoreServerLock
        global gDatabase
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.PauseSequence()")

            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                raise Exception("No sequence running, cannot pause")

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                raise Exception("Not the user running the sequence, cannot pause")

            # Pause the sequence run
            gRunSequence.pauseRun()
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.PauseSequence() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_ContinueSequence(self, sUsername):
        """Continues a paused run"""
        global gCoreServerLock
        global gDatabase
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.ContinueSequence()")

            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                raise Exception("No sequence running, cannot pause")

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                raise Exception("Not the user running the sequence, cannot pause")

            # Continue the sequence run
            gRunSequence.continueRun()
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.ContinueSequence() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_WillSequencePause(self, sUsername):
        """Returns true if the sequence run is flagged to pause, false otherwise"""
        global gCoreServerLock
        global gDatabase
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.WillSequencePause()")

            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                raise Exception("No sequence running, cannot check if sequence will pause")

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                raise Exception("Not the user running the sequence, cannot check if sequence will pause")

            # Check if the run will pause
            pResult = self.SuccessResult(gRunSequence.willRunPause())
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.WillSequencePause() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_IsSequencePaused(self, sUsername):
        """Returns true if the sequence run paused, false otherwise"""
        global gCoreServerLock
        global gDatabase
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.IsSequencePaused()")

            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                raise Exception("No sequence running, cannot check if sequence is paused")

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                raise Exception("Not the user running the sequence, cannot check if sequence is paused")

            # Check the run is paused
            pResult = self.SuccessResult(gRunSequence.isRunPaused())
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.IsSequencePaused() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_ShowAbortSequencePrompt(self, sUsername, bShowAbortPrompt):
        """Displays the abort sequence prompt in the run state"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.ShowAbortSequencePrompt()")

            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                raise Exception("No sequence running, cannot prompt for abort")

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                raise Exception("Not the user running the sequence, cannot prompt for abort")

            # Set the abort prompt flag
            gRunSequence.setShowAbortPrompt(bShowAbortPrompt)
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.ShowAbortSequencePrompt() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_AbortSequence(self, sUsername):
        """Quickly turns off the heaters and terminates the run, leaving the system in its current state"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.AbortSequence()")

            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                raise Exception("No sequence running, cannot abort")

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                raise Exception("Not the user running the sequence, cannot abort")

            # Abort the sequence run
            gRunSequence.abortRun()
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.AbortSequence() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_OverrideTimer(self, sUsername):
        """Overrides the timer if the unit operation has one running"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.OverrideTimer()")

            # Perform additional checks if the user is someone other than the CLI
            if sUsername != "CLI":
                # Make sure the system is running
                if (gRunSequence == None) or not gRunSequence.running:
                    raise Exception("No sequence running, cannot override timer")

                # Make sure we are the user running the system
                if gRunUsername != sUsername:
                    raise Exception("Not the user running the sequence, cannot override timer")

            # Make sure we have a unit operation
            pUnitOperation = gSystemModel.GetUnitOperation()
            if pUnitOperation == None:
                raise Exception("No unit operation, cannot override timer")

            # Deliver the override timer signal to the current unit operation
            pUnitOperation.overrideTimer()
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.OverrideTimer() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_StopTimer(self, sUsername):
        """Stops the unit operation if the timer has been overridden"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.StopTimer()")

            # Perform additional checks if the user is someone other than the CLI
            if sUsername != "CLI":
                # Make sure the system is running
                if (gRunSequence == None) or not gRunSequence.running:
                    raise Exception("No sequence running, cannot stop timer")

                # Make sure we are the user running the system
                if gRunUsername != sUsername:
                    raise Exception("Not the user running the sequence, cannot stop timer")

            # Make sure we have a unit operation
            pUnitOperation = gSystemModel.GetUnitOperation()
            if pUnitOperation == None:
                raise Exception("No unit operation, cannot stop timer")

            # Deliver the stop timer signal to the current unit operation
            pUnitOperation.stopTimer()
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.StopTimer() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_SetSoftErrorDecision(self, sUsername, sDecision):
        """Sets the user's decision on how to handle the soft error"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.SetSoftErrorDecision()")

            # Perform additional checks if the user is someone other than the CLI
            if sUsername != "CLI":
                # Make sure the system is running
                if (gRunSequence == None) or not gRunSequence.running:
                    raise Exception("No sequence running, cannot set soft error decision")

                # Make sure we are the user running the system
                if gRunUsername != sUsername:
                    raise Exception("Not the user running the sequence, cannot set soft error decision")

            # Make sure we have a unit operation
            pUnitOperation = gSystemModel.GetUnitOperation()
            if pUnitOperation == None:
                raise Exception("No unit operation, cannot set soft error decision")

            # Check the unit operation for a soft error
            pUnitOperation.setSoftErrorDecision(sDecision)
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.SetSoftErrorDecision() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_DeliverUserInput(self, sUsername):
        """Delivers user input to the current unit operation"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.DeliverUserInput()")

            # Perform additional check if the user is not the CLI
            if sUsername != "CLI":
                # Make sure the system is running
                if (gRunSequence == None) or not gRunSequence.running:
                    raise Exception("No sequence running, cannot deliver user input")

                # Make sure we are the user running the system
                if gRunUsername != sUsername:
                    raise Exception("Not the user running the sequence, cannot deliver user input")

            # Make sure we have a unit operation
            pUnitOperation = gSystemModel.GetUnitOperation()
            if pUnitOperation == None:
                raise Exception("No unit operation, cannot deliver user input")

            # Deliver the user input to the current unit operation
            pUnitOperation.deliverUserInput()
            pResult = self.SuccessResult()
        except Exception, ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.DeliverUserInput() failed: " + str(ex))
            pResult = self.FailureResult()

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return pResult

    def exposed_CLIExecuteCommand(self, sUsername, sCommand):
        """Executes a command for the CLI"""
        global gCoreServerLock
        global gDatabase
        global gHardwareComm
        global gSystemModel
        global gUnitOperationsWrapper
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLIExecuteCommand(" + sCommand + ")")

            # Execute the command
            sResult = BaseCLI.ExecuteCommandImpl(sCommand, gUnitOperationsWrapper, gSystemModel, gHardwareComm)
        except Exception as ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.CLIExecuteCommand() failed: " + str(ex))
            sResult = "Failed to execute command: " + str(ex)

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return sResult

    def exposed_CLISendCommand(self, sUsername, sCommand):
        """Sends a command for the CLI"""
        global gCoreServerLock
        global gDatabase
        global gHardwareComm
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLISendCommand(" + sCommand + ")")

            # Send the raw command
            sResult = BaseCLI.SendCommandImpl(sCommand, gHardwareComm)
        except Exception as ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.CLISendCommand() failed: " + str(ex))
            sResult = "Failed to send command: " + str(ex)

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return sResult

    def exposed_CLIAbortUnitOperation(self, sUsername):
        """Aborts the current unit operation for the CLI"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLIAbortUnitOperation()")

            # Make sure we have a unit operation
            pUnitOperation = gSystemModel.GetUnitOperation()
            if pUnitOperation == None:
                raise Exception("No unit operation, cannot abort")

            # Deliver the abort signal to the current unit operation
            pUnitOperation.setAbort()
            bResult = True
        except Exception as ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.CLIAbortUnitOperation() failed: " + str(ex))
            bResult = False

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return bResult

    def exposed_CLIGetState(self, sUsername):
        """Gets the state for the CLI"""
        global gCoreServerLock
        global gDatabase
        global gSystemModel
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLIGetState()")

            # Return the system state
            sResult = BaseCLI.GetStateImpl(gSystemModel)
        except Exception as ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.CLIGetState() failed: " + str(ex))
            sResult = "Failed to get system state: " + str(ex)

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return sResult

    def exposed_CLIBroadcast(self, sUsername, sMessage):
        """Gets the state for the CLI"""
        global gCoreServerLock
        global gDatabase
        global gMessaging
        bLocked = False
        try:
            # Acquire the lock
            gCoreServerLock.Acquire(1)
            bLocked = True
            gDatabase.SystemLog(LOG_INFO, sUsername, "CoreServerService.CLIBroadcast(" + sMessage + ")")

            # Create the messaging object and broadcast the message
            if gMessaging == None:
                gMessaging = Messaging("System", gDatabase)
            gMessaging.broadcastMessage(sMessage)
            bResult = True
        except Exception as ex:
            # Log the error
            gDatabase.SystemLog(LOG_ERROR, sUsername, "CoreServerService.CLIBroadcast() failed: " + str(ex))
            gMessaging = None
            bResult = False

        # Release the lock and return
        if bLocked:
            gCoreServerLock.Release()
        return bResult

    def SuccessResult(self, pReturn = None):
        """Formats a successful result"""
        if pReturn != None:
            return {"success":True, "return":pReturn}
        else:
            return {"success":True}

    def FailureResult(self):
        """Formats a failed result"""
        return {"success":False}

    def FormatTime(self, nTime):
        """Format the time to a string"""
        nSeconds = int(nTime) % 60
        nMinutes = int((nTime - nSeconds) / 60) % 60
        nHours = int((((nTime - nSeconds) / 60) - nMinutes) / 60)
        sTime = ""
        if nHours != 0:
            sTime += str(nHours) + ":"
        if nMinutes < 10:
            sTime += "0"
        sTime += str(nMinutes) + "'"
        if nSeconds < 10:
            sTime += "0"
        sTime += str(nSeconds) + "\""
        return sTime

# Function that create an initial run state
def InitialRunState():
    pRunState = {"type":"runstate"}
    pRunState["description"] = ""
    pRunState["status"] = ""
    pRunState["running"] = False
    pRunState["prompt"] = {"type":"promptstate",
        "show":False,
        "title":""}
    pRunState["username"] = ""
    pRunState["sequenceid"] = 0
    pRunState["componentid"] = 0
    pRunState["time"] = ""
    pRunState["timedescription"] = ""
    pRunState["useralert"] = ""
    pRunState["unitoperationbutton"] = {"type":"button",
        "text":"",
        "id":""}
    pRunState["waitingforuserinput"] = False
    pRunState["runcomplete"] = False
    return pRunState

# Core server daemon exit function
gCoreServerDaemon = None
def OnExit(pCoreServerDaemon, signal, func=None):
    global gCoreServerDaemon
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
        global gCoreServerLock
        global gServerStateLock
        global gDatabase
        global gHardwareComm
        global gSystemModel
        global gUnitOperationsWrapper
        global gCoreServerDaemon
        global gMessaging
        pCoreServerThread = None
        while not self.bTerminate:
            try:
                # Create the locks and database connection
                gCoreServerLock = TimedLock.TimedLock()
                gServerStateLock = TimedLock.TimedLock()
                gDatabase = DBComm()
                gDatabase.Connect()
                gDatabase.SystemLog(LOG_INFO, "System", "CoreServer starting")

                # Create the hardware layer and system model
                gHardwareComm = HardwareComm()
                gHardwareComm.StartUp()
                gSystemModel = SystemModel(gHardwareComm, gDatabase)
                gSystemModel.StartUp()

                # Create the unit operations wrapper
                gUnitOperationsWrapper = UnitOperationsWrapper(gSystemModel, gDatabase)

                # Create the core server and error message handler
                pLogger = logging.getLogger("rpyc")
                pLogger.setLevel(logging.ERROR)
                pLogHandler = RpycLogHandler()
                pLogger.addHandler(pLogHandler)
                pCoreServer = ThreadedServer(CoreServerService, port = 18862, logger = pLogger)

                # Start the core server thread
                pCoreServerThread = CoreServerThread()
                pCoreServerThread.SetParameters(pCoreServer)
                pCoreServerThread.setDaemon(True)
                pCoreServerThread.start()

                # Install the kill signal handler
                signal.signal(signal.SIGTERM, OnExit)
                gDatabase.SystemLog(LOG_INFO, "System", "CoreServer started")

                # Run until we get the signal to stop
                while not self.bTerminate:
                    gSystemModel.CheckForError()
                    pCoreServerThread.CheckForError()
                    time.sleep(0.25)
                gDatabase.SystemLog(LOG_INFO, "System", "CoreServer received quit signal")
            except Exception as ex:
                # Log the error
                sError = "CoreServer failed: " + str(ex)
                if gDatabase != None:
                    gDatabase.SystemLog(LOG_ERROR, "System", sError)
                else:
                    print sError
            finally:
                if pCoreServerThread != None:
                    pCoreServerThread.Terminate()
                    pCoreServerThread.join()
                    pCoreServerThread = None
                if gSystemModel != None:
                    gSystemModel.ShutDown()
                    gSystemModel = None
                if gHardwareComm != None:
                    gHardwareComm.ShutDown()
                    gHardwareComm = None
                if gDatabase != None:
                    gDatabase.SystemLog(LOG_INFO, "System", "CoreServer stopped")
                    gDatabase.Disconnect()
                    gDatabase = None
                if gCoreServerLock != None:
                    gCoreServerLock = None
                if gServerStateLock != None:
                    gServerStateLock = None

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

