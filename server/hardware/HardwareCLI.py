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
            else:
                pParameters[1] = pParameters[1].strip('"')
                pParameters[1] = pParameters[1].strip("'")
                pFunction(pHardwareComm, pParameters[0], pParameters[1])
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
            print "  list names      List the hardware names"
            print "  list positions  List the motor positions"
            print "  get state       Displays the current state of the system"
            print "  send help       Display a brief description of the PLC command format" 
            print "  send [command]  Send the raw command to the PLC"
        elif sCommand == "list functions":
            # Yes, it's a wall of text.  We could use introspection for the function names but it gets even messier that way because we
            # don't want to list all of our functions
            print "Recognized functions:"
            print "  Vacuum system functions:"
            print "    Not implemented: VacuumSystemOn()"
            print "    Not implemented: VacuumSystemOff()"
            print "  Cooling system functions:"
            print "    Not implemented: CoolingSystemOn()"
            print "    Not implemented: CoolingSystemOff()"
            print "  Pressure regulator functions:"
            print "    Not implemented: PressureRegulatorOn(sName)"
            print "    Not implemented: PressureRegulatorOff(sName)"
            print "    Not implemented: SetPressureRegulator(sName, fPressure)"
            print "  Reagent robot functions:"
            print "    Not implemented: MoveReagentRobot(sPositionName)"
            print "    GripperUp()"
            print "    GripperDown()"
            print "    GripperOpen()"
            print "    GripperClose()"
            print "  F-18 functions:"
            print "    LoadF18Start()"
            print "    LoadF18Stop()"
            print "    EluteF18Start()"
            print "    EluteF18Stop()"
            print "  Reactor functions:"
            print "    Not implemented: MoveReactor(sPositionName)"
            print "    ReactorUp(sName)"
            print "    ReactorDown(sName)"
            print "    ReactorEvaporateStart(sName)"
            print "    ReactorEvaporateStop(sName)"
            print "    ReactorTransferStart(sName)"
            print "    ReactorTransferStop(sName)"
            print "    ReactorReagentTransferStart(sName)"
            print "    ReactorReagentTransferStop(sName)"
            print "    ReactorStopcockOpen(sName)"
            print "    ReactorStopcockClose(sName)"
            print "  Temperature controller functions:"
            print "    SetHeater(sName, fSetPoint)"
            print "  Stir motor functions:"
            print "    Not implemented: SetMotorSpeed(sName, nMotorSpeed)"
            print "  Radiation detector functions:"
            print "    Not implemented: ReadRadiationDetector(sName)"
        elif sCommand == "list names":
            # We're not reading this from the INI file because only certain values in there are valid and only for certain functions.  So in the
            # end it's just less confusing to print them here manually
            print "Recognized hardware names:"
            print "  Pressure regulator names:"
            print "    PressureRegulator1"
            print "    PressureRegulator2"
            print "  Reactor names:"
            print "    Reactor1"
            print "    Reactor2"
            print "    Reactor3"
            print "  Reactor reagent transfer names:"
            print "    [reactor]_Reagent1"
            print "    [reactor]_Reagent2"
            print "  Reactor stopcock names:"
            print "    [reactor]_Stopcock1"
            print "    [reactor]_Stopcock2"
            print "    [reactor]_Stopcock3"
            print "  Temperature controller names:"
            print "    [reactor]_TemperatureController1"
            print "    [reactor]_TemperatureController2"
            print "    [reactor]_TemperatureController3"
            print "  Stir motors and radiation detectors are named by just the reactor"
        elif sCommand == "list positions":
            # I've gone this far, might as well make this one embedded text as well
            print "Recognized robot positions:"
            print "  Reagent robot positions:"
            print "    [reactor]_Reagent1"
            print "    ..."
            print "    [reactor]_Reagent10"
            print "    [reactor]_ReagentDelivery1"
            print "    [reactor]_ReagentDelivery2"
            print "  Reactor positions:"
            print "    [reactor]_Install"
            print "    [reactor]_Transfer"
            print "    [reactor]_React1"
            print "    [reactor]_Add"
            print "    [reactor]_React2"
            print "    [reactor]_Evaporate"
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
