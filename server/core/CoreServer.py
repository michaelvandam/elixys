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
sys.path.append("../database")
sys.path.append("../hardware")
sys.path.append("../cli")
sys.path.append("unitoperations")
from DBComm import DBComm
from HardwareComm import HardwareComm
from SystemModel import SystemModel
import Utilities
import json
import Sequences
import UnitOperation
import BaseCLI
from UnitOperationsWrapper import UnitOperationsWrapper
import os

# Suppress rpyc warning messages
import logging
logging.basicConfig(level=logging.ERROR)

# Create the database and sequence manager
gDatabase = DBComm()
gDatabase.Connect()
gSequenceManager = SequenceManager(gDatabase)

# Create the hardware layer and system model
gRootDirectory = "../"
gHardwareComm = HardwareComm(gRootDirectory)
gHardwareComm.StartUp()
gSystemModel = SystemModel(gHardwareComm, gRootDirectory + "core/")
gSystemModel.StartUp()

# Create the unit operations wrapper
gUnitOperationsWrapper = UnitOperationsWrapper(gSystemModel)

# Initialize the run state
gRunUsername = ""
gRunSequence = None

# Core server service
class CoreServerService(rpyc.Service):
    def on_connect(self):
        """Invoked when a client connects"""
        global gDatabase
        gDatabase.Log("System", "CoreServerService.connect()")
        # Allow pickling on this connection for proper data transfer
        self._conn._config["allow_pickle"] = True
 
    def on_disconnect(self):
        """Invoked when a client disconnects"""
        global gDatabase
        gDatabase.Log("System", "CoreServerService.disconnect()")

    def exposed_GetServerState(self, sUsername):
        """Returns the state of the server"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.Log(sUsername, "CoreServerService.GetServerState()")

        # Format the run state
        pServerState = {"type":"serverstate"}
        pServerState["runstate"] = {"type":"runstate"}
        if (gRunSequence != None) and gRunSequence.running:
            pUnitOperation = gSystemModel.GetUnitOperation()
            if pUnitOperation != None:
                pServerState["runstate"]["status"] = pUnitOperation.status
                pServerState["runstate"]["prompt"] = {"type":"promptstate"}
                if pUnitOperation.waitingForUserInput:
                    pServerState["runstate"]["prompt"]["screen"] = "PROMPT_UNITOPERATION"
                    pServerState["runstate"]["prompt"]["show"] = True
                    pServerState["runstate"]["prompt"]["title"] = pUnitOperation.userInputTitle
                    pServerState["runstate"]["prompt"]["text1"] = pUnitOperation.userInputText
                    pServerState["runstate"]["prompt"]["text2"] = ""
                    if sUsername == gRunUsername:
                        pServerState["runstate"]["prompt"]["buttons"] = [{"type":"button",
                            "text":"OK",
                            "id":"OK"}]
                    else:
                        pServerState["runstate"]["prompt"]["buttons"] = [{"type":"button",
                            "text":"Back",
                            "id":"BACK"}]
                else:
                    pServerState["runstate"]["prompt"]["show"] = False
            else:
                pServerState["runstate"]["status"] = ""
                pServerState["runstate"]["prompt"] = {"type":"promptstate",
                    "show":False}
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

        # Load the hardware state
        pModel = gSystemModel.LockSystemModel()
        sReagentRobotPositionName1, sReagentRobotPositionName2 = pModel["ReagentDelivery"].getCurrentPositionName(False)
        bGripperActuatorUp = pModel["ReagentDelivery"].getCurrentGripperUp(False)
        bGripperActuatorDown = pModel["ReagentDelivery"].getCurrentGripperDown(False)
        if bGripperActuatorUp and not bGripperActuatorDown:
            sReagentRobotGripperActuator = "Up"
        elif not bGripperActuatorUp and bGripperActuatorDown:
            sReagentRobotGripperActuator = "Down"
        else:
            sReagentRobotGripperActuator = "Indeterminate"
        bGripperOpen = pModel["ReagentDelivery"].getCurrentGripperOpen(False)
        bGripperClose = pModel["ReagentDelivery"].getCurrentGripperClose(False)
        if bGripperOpen and not bGripperClose:
            sReagentRobotGripper = "Open"
        elif not bGripperOpen and bGripperClose:
            sReagentRobotGripper = "Close"
        else:
            sReagentRobotGripper = "Indeterminate"
        bGasTransferActuatorUp = pModel["ReagentDelivery"].getCurrentGasTransferUp(False)
        bGasTransferActuatorDown = pModel["ReagentDelivery"].getCurrentGasTransferDown(False)
        if bGasTransferActuatorUp and not bGasTransferActuatorDown:
            sReagentRobotGasTransferActuator = "Up"
        elif not bGasTransferActuatorUp and bGasTransferActuatorDown:
            sReagentRobotGasTransferActuator = "Down"
        else:
            sReagentRobotGasTransferActuator = "Indeterminate"

        # Format the hardware state
        pServerState["hardwarestate"] = {"type":"hardwarestate"}
        pServerState["hardwarestate"]["pressureregulators"] = []
        pServerState["hardwarestate"]["pressureregulators"].append({"type":"pressureregulatorstate",
            "name":"Pneumatics",
            "pressure":pModel["PressureRegulator1"].getCurrentPressure(False)})
        pServerState["hardwarestate"]["pressureregulators"].append({"type":"pressureregulatorstate",
            "name":"Gas",
            "pressure":pModel["PressureRegulator2"].getCurrentPressure(False)})
        pServerState["hardwarestate"]["cooling"] = pModel["CoolingSystem"].getCoolingSystemOn(False)
        pServerState["hardwarestate"]["vacuum"] = {"type":"vacuumstate"}
        pServerState["hardwarestate"]["vacuum"]["on"] = pModel["VacuumSystem"].getVacuumSystemOn(False)
        pServerState["hardwarestate"]["vacuum"]["vacuum"] = pModel["VacuumSystem"].getVacuumSystemPressure(False)
        pServerState["hardwarestate"]["valves"] = {"type":"valvesstate"}
        pServerState["hardwarestate"]["valves"]["gastransfervalve"] = pModel["Valves"].getGasTransferValveOpen(False)
        pServerState["hardwarestate"]["valves"]["f18loadvalve"] = pModel["Valves"].getF18LoadValveOpen(False)
        pServerState["hardwarestate"]["valves"]["hplcloadvalve"] = pModel["Valves"].getHPLCLoadValveOpen(False)
        pServerState["hardwarestate"]["reagentrobot"] = {"type":"reagentrobotstate"}
        pServerState["hardwarestate"]["reagentrobot"]["position"] = {"type":"reagentrobotposition",
            "name1":sReagentRobotPositionName1,
            "name2":sReagentRobotPositionName2}
        pServerState["hardwarestate"]["reagentrobot"]["gripperactuator"] = sReagentRobotGripperActuator
        pServerState["hardwarestate"]["reagentrobot"]["gripper"] = sReagentRobotGripper
        pServerState["hardwarestate"]["reagentrobot"]["gastransferactuator"] = sReagentRobotGasTransferActuator

        # Determine if we are in demo mode
        sDemoFile = gRootDirectory + "demomode"
        if not os.path.isfile(sDemoFile):
            bDemoMode = False
        else:
            bDemoMode = True
            
        # Format the hardware state associated with each reactor
        pServerState["hardwarestate"]["reactors"] = []
        nReactorCount = gDatabase.GetConfiguration("System")["reactors"]
        for nReactor in range(1, nReactorCount + 1):
            # Load the reactor hardware state
            pReactorModel = pModel["Reactor" + str(nReactor)]
            bReactorUp = pReactorModel["Motion"].getCurrentReactorUp(False)
            bReactorDown = pReactorModel["Motion"].getCurrentReactorDown(False)
            if bReactorUp and not bReactorDown:
                sReactorPosition = "Up"
            elif not bReactorUp and bReactorDown:
                sReactorPosition = "Down"
            else:
                sReactorPosition = "Indeterminate"
            nTransferPosition = pReactorModel["Stopcock1"].getPosition(False)
            if nTransferPosition == UnitOperation.TRANSFERTRAP[0]:
                sTransferPosition = "Waste"
            elif nTransferPosition == UnitOperation.TRANSFERELUTE[0]:
                sTransferPosition = "Out"
            else:
                sTransferPosition = "Indeterminate"

            # Format the reactor hardware state
            pReactor = {"type":"reactorstate"}
            pReactor["number"] = nReactor
            fTemperature1 = pReactorModel["Thermocouple"].getHeater1CurrentTemperature(False)
            fTemperature2 = pReactorModel["Thermocouple"].getHeater2CurrentTemperature(False)
            fTemperature3 = pReactorModel["Thermocouple"].getHeater3CurrentTemperature(False)
            pReactor["temperature"] = (fTemperature1 + fTemperature2 + fTemperature3) / 3
            pReactor["position"] = {"type":"reactorposition",
                "horizontal":pModel["Reactor" + str(nReactor)]["Motion"].getCurrentPosition(False),
                "vertical":sReactorPosition}
            pReactor["activity"] = 0
            pReactor["activitytime"] = ""
            pReactor["transferposition"] = sTransferPosition
            pReactor["stirspeed"] = pReactorModel["Stir"].getCurrentSpeed(False)
            if not bDemoMode:
               pReactor["video"] = "Reactor" + str(nReactor)
            else:
               pReactor["video"] = "mp4:elixys.mp4"

            # Format additional fields for reactor 1
            if nReactor == 1:
                nColumnPosition1 = pReactorModel["Stopcock2"].getPosition(False)
                nColumnPosition2 = pReactorModel["Stopcock3"].getPosition(False)
                if (nColumnPosition1 == UnitOperation.F18TRAP[1]) and (nColumnPosition1 == UnitOperation.F18TRAP[2]):
                    sColumnPosition = "Load"
                if (nColumnPosition1 == UnitOperation.F18ELUTE[1]) and (nColumnPosition1 == UnitOperation.F18ELUTE[2]):
                    sColumnPosition = "Elute"
                else:
                    sColumnPosition = "Indeterminate"
                pReactor["columnposition"] = sColumnPosition

            # Append the reactor
            pServerState["hardwarestate"]["reactors"].append(pReactor)

        # Unlock the model and return the server state as a JSON string
        gSystemModel.UnlockSystemModel()
        return json.dumps(pServerState)

    def exposed_RunSequence(self, sUsername, nSequenceID):
        """Loads a sequence from the database and runs it"""
        global gDatabase
        global gSystemModel
        global gSequenceManager
        global gRunUsername
        global gRunSequence
        gDatabase.Log(sUsername, "CoreServerService.RunSequence(" + str(nSequenceID) + ")")

        # Make sure we aren't already running a sequence
        if gRunSequence != None:
          if gRunSequence.running:
            gDatabase.Log(sUsername, "A sequence is already running, cannot run another")
            return False

        # Create and start the sequence
        gRunSequence = Sequences.Sequence(sUsername, nSequenceID, gSequenceManager, gSystemModel)
        gRunSequence.setDaemon(True)
        gRunSequence.start()
        gRunUsername = sUsername
        return True

    def exposed_PauseSequence(self, sUsername):
        """Causes the system to pause after the current unit operation is complete"""
        global gDatabase
        gDatabase.Log(sUsername, "CoreServerService.Pause()")
        return False

    def exposed_ContinueSequence(self, sUsername):
        """Continues a paused run"""
        global gDatabase
        gDatabase.Log(sUsername, "CoreServerService.Continue()")
        return False

    def exposed_AbortSequence(self, sUsername):
        """Quickly turns off the heaters and terminates the run, leaving the system in its current state"""
        global gDatabase
        global gSystemModel
        global gRunUsername
        global gRunSequence
        gDatabase.Log(sUsername, "CoreServerService.AbortSequence()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.Log(sUsername, "No sequence running, cannot abort")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.Log(sUsername, "Not the user running the sequence, cannot abort")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.Log(sUsername, "No unit operation, cannot abort")
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
        gDatabase.Log(sUsername, "CoreServerService.PauseTimer()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.Log(sUsername, "No sequence running, cannot pause timer")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.Log(sUsername, "Not the user running the sequence, cannot pause timer")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.Log(sUsername, "No unit operation, cannot pause timer")
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
        gDatabase.Log(sUsername, "CoreServerService.ContinueTimer()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.Log(sUsername, "No sequence running, cannot continue timer")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.Log(sUsername, "Not the user running the sequence, cannot continue timer")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.Log(sUsername, "No unit operation, cannot continue timer")
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
        gDatabase.Log(sUsername, "CoreServerService.StopTimer()")

        # Perform additional checks if the user is someone other than the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.Log(sUsername, "No sequence running, cannot stop timer")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.Log(sUsername, "Not the user running the sequence, cannot stop timer")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.Log(sUsername, "No unit operation, cannot stop timer")
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
        gDatabase.Log(sUsername, "CoreServerService.DeliverUserInput()")

        # Perform additional check if the user is not the CLI
        if sUsername != "CLI":
            # Make sure the system is running
            if (gRunSequence == None) or not gRunSequence.running:
                gDatabase.Log(sUsername, "No sequence running, cannot deliver user input")
                return False

            # Make sure we are the user running the system
            if gRunUsername != sUsername:
                gDatabase.Log(sUsername, "Not the user running the sequence, cannot deliver user input")
                return False

        # Make sure we have a unit operation
        pUnitOperation = gSystemModel.GetUnitOperation()
        if pUnitOperation == None:
            gDatabase.Log(sUsername, "No unit operation, cannot deliver user input")
            return False

        # Deliver the user input to the current unit operation
        pUnitOperation.deliverUserInput()
        return True

    def exposed_CLIConnectToStateMonitor(self, sUsername):
        """Sets the state monitor"""
        global gDatabase
        global gSystemModel
        gDatabase.Log(sUsername, "CoreServerService.CLISetStateMonitor()")

        # Try to connect to the state monitor
        try:
            pStateMonitor = rpyc.connect("localhost", 18861)
            gSystemModel.SetStateMonitor(pStateMonitor)
            return ""
        except socket.error, ex:
            print "Warning: failed to connect to state monitor, no output will be displayed"

    def exposed_CLIExecuteCommand(self, sUsername, sCommand):
        """Executes a command for the CLI"""
        global gDatabase
        global gHardwareComm
        global gSystemModel
        global gUnitOperationsWrapper
        gDatabase.Log(sUsername, "CoreServerService.CLIExecuteCommand(" + sCommand + ")")

        # Execute the command
        try:
            return BaseCLI.ExecuteCommandImpl(sCommand, gUnitOperationsWrapper, gSystemModel, gHardwareComm)
        except Exception as ex:
            return "Failed to execute command: " + str(ex)

    def exposed_CLISendCommand(self, sUsername, sCommand):
        """Sends a command for the CLI"""
        global gDatabase
        global gHardwareComm
        gDatabase.Log(sUsername, "CoreServerService.CLISendCommand(" + sCommand + ")")

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
        gDatabase.Log(sUsername, "CoreServerService.CLIGetState()")

        # Return the system state
        try:
            return BaseCLI.GetStateImpl(gSystemModel)
        except Exception as ex:
            return "Failed to get system state: " + str(ex)

# Main function
if __name__ == "__main__":
    try:
        # Connect to the database
        gDatabase.Log("System", "CoreServer starting")

        # Create the core server
        pCoreServer = ThreadedServer(CoreServerService, port = 18862)
    
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
        time.sleep(1)
        gDatabase.Log("System", "CoreServer stopped")
    except Exception as ex:
        # Log the error
        gDatabase.Log("System", "CoreServer encountered an error: " + str(ex))

