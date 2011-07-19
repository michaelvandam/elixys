""" HardwareCLI.py

Implements a CLI interface to the Elixys hardware """

### Imports
import inspect
from HardwareComm import HardwareComm
import time

# Parses and executes the given command
def ExecuteCommand(sCommand, pHardwareComm):
    try:
        # Ignore empty commands
        if sCommand == "":
            return

        # Strip off the trailing parenthesis from the command and split into the function name and parameters
        pCommandComponents = sCommand.strip(")").split("(")
        sFunctionName = pCommandComponents[0]

        # Make sure the function name exists
        if not hasattr(HardwareComm, sFunctionName):
            raise Exception("Unknown function " + sFunctionName)

        # Make sure the function name maps to a callable object
        pFunction = getattr(HardwareComm, sFunctionName)
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

        # Strip any quotes from the parameters and call the function
        if nParameters == 0:
            pFunction(pHardwareComm)
        else:
            pParameters[0] = pParameters[0].strip('"')
            pParameters[0] = pParameters[0].strip("'")
            if nParameters == 1:
                pFunction(pHardwareComm, pParameters[0])
            elif nParameters == 2:
                pParameters[1] = pParameters[1].strip('"')
                pParameters[1] = pParameters[1].strip("'")
                pFunction(pHardwareComm, pParameters[0], pParameters[1])
            elif nParameters == 3:
                pParameters[1] = pParameters[1].strip('"')
                pParameters[1] = pParameters[1].strip("'")
                pParameters[2] = pParameters[2].strip('"')
                pParameters[2] = pParameters[2].strip("'")
                pFunction(pHardwareComm, pParameters[0], pParameters[1], pParameters[2])
            else:
                raise Exception("Too many arguments");
    except Exception as ex:
        # Display the error
        print "Error: " + str(ex)

# Parses and sends the raw command
def SendCommand(sCommand, pHardwareComm):
    # Extract the command and send it as a raw packet
    pCommandComponents = sCommand.split(" ")
    pHardwareComm._HardwareComm__SendRawCommand(pCommandComponents[1])

# Main CLI function
if __name__ == "__main__":
    # Fire up an instance of the hardware comm layer
    pHardwareComm = HardwareComm()
    pHardwareComm.StartUp();

    # CLI loop
    print "Elixys Hardware Communications Layer CLI"
    print "Type help for available commands."
    while True:
        # Get input and strip newlines
        sCommand = raw_input(">>> ").strip("\r\n")

        # Handle commands
        if sCommand == "exit":
            break
        elif sCommand == "help":
            print "Recognized commands:"
            print "  list functions  Lists available function"
            print "  list positions  List the motor positions"
            print "  get state       Displays the current state of the system"
            print "  send help       Display a brief description of the PLC command format" 
            print "  send [command]  Send the raw command to the PLC"
        elif sCommand == "list functions":
            # Yes, it's a wall of text.  We could use introspection for the function names but it gets even messier that way because we
            # don't want to list all of our functions
            print "Recognized functions:"
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
        elif sCommand == "list positions":
            # I've gone this far, might as well make this one embedded text as well
            print "Recognized reactor positions:"
            print "  Install"
            print "  Transfer"
            print "  React1"
            print "  Add"
            print "  React2"
            print "  Evaporate"
        elif sCommand == "get state":
            # Request the state from the hardware
            pHardwareComm.UpdateState()

            # Sleep a bit and display the state
            time.sleep(0.25)
        elif sCommand == "send help":
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
        elif sCommand.startswith("send "):
            # Attempt to send the command
            SendCommand(sCommand, pHardwareComm)

            # Sleep a bit to give the PLC a chance to response before we display the carrot
            time.sleep(0.25)
        else:
            # Attempt to execute the command
            ExecuteCommand(sCommand, pHardwareComm)

            # Sleep a bit to give the PLC a chance to response before we display the carrot
            time.sleep(0.25)

    # Clean up the hardware comm layer
    pHardwareComm.ShutDown()
