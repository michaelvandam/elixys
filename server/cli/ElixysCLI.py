""" ElixysCLI.py

Implements a CLI interface to the Elixys system """

### Imports
import inspect
import time
import sys
sys.path.append("../hardware/")
sys.path.append("../core/")
from HardwareComm import HardwareComm
from SystemModel import SystemModel
from UnitOperationsWrapper import UnitOperationsWrapper

# Parses and executes the given command
def ExecuteCommand(sCommand, pUnitOperationsWrapper, pHardwareComm):
    try:
        # Ignore empty commands
        if sCommand == "":
            return

        # Strip off the trailing parenthesis from the command and split into the function name and parameters
        pCommandComponents = sCommand.strip(")").split("(")
        sFunctionName = pCommandComponents[0]

        # Make sure the function name exists on either the unit operations wrapper or the hardware layer
        if hasattr(UnitOperationsWrapper, sFunctionName):
            Object = UnitOperationsWrapper
            pObject = pUnitOperationsWrapper
        elif hasattr(HardwareComm, sFunctionName):
            Object = HardwareComm
            pObject = pHardwareComm
        else:
            raise Exception("Unknown function " + sFunctionName)

        # Make sure the function name maps to a callable object
        pFunction = getattr(Object, sFunctionName)
        if not callable(pFunction):
            raise Exception(sFunctionName + " is not a function")

        # Make sure we have the correct number of arguments
        pParameters = pCommandComponents[1].split(",")
        nParameters = len(pParameters)
        if (nParameters == 1) and (pParameters[0] == ""):
            nParameters = 0
        pFunctionParameters = inspect.getargspec(pFunction).args
        if (nParameters + 1) != len(pFunctionParameters):
            raise Exception("Incorrect number of arguments for " + sFunctionName)

        # Prepare each function parameter
        for nIndex in range(0, nParameters):
            # Strip any quotes and whitespace
            pParameters[nIndex] = pParameters[nIndex].strip('"')
            pParameters[nIndex] = pParameters[nIndex].strip("'")
            pParameters[nIndex] = pParameters[nIndex].strip()
            
            # Interpret any integers as such
            try:
                pParameters[nIndex] = int(pParameters[nIndex])
                continue;
            except ValueError:
                pass

            # Interpret any floats as such
            try:
                pParameters[nIndex] = float(pParameters[nIndex])
                continue;
            except ValueError:
                pass

        # Call the function
        if nParameters == 0:
            pFunction(pObject)
        elif nParameters == 1:
            pFunction(pObject, pParameters[0])
        elif nParameters == 2:
            pFunction(pObject, pParameters[0], pParameters[1])
        elif nParameters == 3:
            pFunction(pObject, pParameters[0], pParameters[1], pParameters[2])
        elif nParameters == 4:
            pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3])
        elif nParameters == 5:
            pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4])
        elif nParameters == 6:
            pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4], pParameters[5])
        elif nParameters == 7:
            pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4], pParameters[5], pParameters[6])
        else:
            raise Exception("Too many arguments");
    except Exception as ex:
        # Display the error
        print "Failed to execute command: " + str(ex)

# Parses and sends the raw command
def SendCommand(sCommand, pHardwareComm):
    # Extract the command and send it as a raw packet
    pCommandComponents = sCommand.split(" ")
    pHardwareComm._HardwareComm__SendRawCommand(pCommandComponents[1])

# Main CLI function
if __name__ == "__main__":
    # Create the hardware layer
    pHardwareComm = HardwareComm()
    pHardwareComm.StartUp()
  
    # Create the system model
    pSystemModel = SystemModel(pHardwareComm)
    pSystemModel.StartUp()
    
    # Create the unit operations wrapper
    pUnitOperationsWrapper = UnitOperationsWrapper(pSystemModel)

    # CLI loop
    print "Elixys Command Line Interface"
    print "Type help for available commands."
    while True:
        # Get input and strip newlines
        sCommand = raw_input(">>> ").strip("\r\n")

        # Handle commands
        if sCommand == "exit":
            break
        elif sCommand == "help":
            print "Recognized commands:"
            print "  help unit operations   Lists available unit operation functions"
            print "  help hardware          Lists available hardware functions"
            print "  help send              Display a brief description of the PLC command format" 
            print "  get state              Displays the current state of the system"
            print "  send [command]         Send the raw command to the PLC"
        elif sCommand == "help unit operations":
            # List the recognized unit operations
            print "Recognized unit operations:"
            print "  React(nReactor, nReactionTemperature, nReactionTime, nFinalTemperature, nReactPosition, nStirSpeed)"
            print "  Add(nReactor, nReagentReactor, nReagentPosition, nReagentDeliveryPosition)"
            print "  Evaporate(nReactor, nEvaporationTemperature, nEvaporationTime, nFinalTemperature, nStirSpeed)"
            print "  Install(nReactor)"
            print "  TransferToHPLC(nReactor, nStopcockPosition)"
            print "  TransferElute(self, nReactor, nStopcockPosition)"
            print "  Transfer(nReactor, nStopcockPosition, nTransferReactorID)"
            print "  UserInput(sUserMessage, bIsCheckBox, sDescription)"
            print "  DetectRadiation()"
        elif sCommand == "help hardware":
            # Yes, it's a wall of text.  We could use introspection for the function names but it gets even messier that way because we
            # don't want to list all of our functions
            print "Recognized hardware functions:"
            print "  Cooling system functions:"
            print "    CoolingSystemOn()"
            print "    CoolingSystemOff()"
            print "  Pressure regulator functions:"
            print "    SetPressureRegulator(nPressureRegulator, fPressure)"
            print "  Reagent robot functions:"
            print "    MoveRobotToReagent(nReactor, nReagent)"
            print "    MoveRobotToDelivery(nReactor, nPosition)"
            print "    GripperUp()"
            print "    GripperDown()"
            print "    GripperOpen()"
            print "    GripperClose()"
            print "  F-18 functions:"
            print "    LoadF18Start()"
            print "    LoadF18Stop()"
            print "    EluteF18Start()"
            print "    EluteF18Stop()"
            print "  HPLC functions:"
            print "    LoadHPLCStart()"
            print "    LoadHPLCStop()"
            print "  Reactor functions:"
            print "    MoveReactor(nReactor, sPositionName)"
            print "      Recognized position names: "
            print "        Install"
            print "        Transfer"
            print "        React1"
            print "        Add"
            print "        React2"
            print "        Evaporate"
            print "    ReactorUp(nReactor)"
            print "    ReactorDown(nReactor)"
            print "    ReactorEvaporateStart(nReactor)"
            print "    ReactorEvaporateStop(nReactor)"
            print "    ReactorTransferStart(nReactor)"
            print "    ReactorTransferStop(nReactor)"
            print "    ReactorReagentTransferStart(nReactor, nPosition)"
            print "    ReactorReagentTransferStop(nReactor, nPosition)"
            print "    ReactorStopcockOpen(nReactor, nStopcock)"
            print "    ReactorStopcockClose(nReactor, nStopcock)"
            print "  Temperature controller functions:"
            print "    HeaterOn(nReactor, nHeater)"
            print "    HeaterOff(nReactor, nHeater)"
            print "    SetHeater(nReactor, nHeater, fSetPoint)"
            print "  Stir motor functions:"
            print "    SetMotorSpeed(nReactor, nMotorSpeed)"
            print "  Radiation detector functions:"
            print "    Not implemented: ReadRadiationDetector(nReactor)"
            print "  Robot utility functions:"
            print "    HomeRobots()"
            print "    DisableRobots()"
            print "    EnableRobots()"
            print "    DisableReactorRobot(nReactor)"
            print "    EnableReactorRobot(nReactor)"
        elif sCommand == "help send":
            # Display a brief description of the PLC command format
            print "Command format:"
            print "    [cccc][xx][xxxxxx][xxxx]"
            print "  Where [cccc] can be:"
            print "    0101 - Read Memory Area" 
            print "    0102 - Write Memory Area"
            print "    0402 - STOP - puts system in program mode"
            print "    0501 - Controller Read Data"
            print "    0601 - Controller Read Status"
            print "    0701 - Controller Read Clock"
            print "  Example:"
            print "    0101800000020001"
        elif sCommand == "get state":
            # Dump the state to standard out
            print pSystemModel.DumpStateToString()
        elif sCommand.startswith("send "):
            # Attempt to send the command
            SendCommand(sCommand, pHardwareComm)

            # Sleep a bit to give the PLC a chance to response before we display the input prompt
            time.sleep(0.25)
        else:
            # Attempt to execute the command
            ExecuteCommand(sCommand, pUnitOperationsWrapper, pHardwareComm)

            # Sleep a bit to give the PLC a chance to response before we display the input prompt
            time.sleep(0.25)

    # Clean up
    pSystemModel.ShutDown()
    pHardwareComm.ShutDown()
