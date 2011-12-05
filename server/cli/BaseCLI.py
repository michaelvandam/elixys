""" BaseCLI.py

Base class for the Elixys and CoreServer CLIs"""

### Imports
import threading
import time
import inspect
import sys
sys.path.append("../hardware/")
sys.path.append("../core/")
from HardwareComm import HardwareComm
from UnitOperationsWrapper import UnitOperationsWrapper

# ExecuteCommand implementation
def ExecuteCommandImpl(sCommand, pUnitOperationsWrapper, pSystemModel, pHardwareComm):
    """Parses and executes the given command"""
    try:
        # Ignore empty commands
        if sCommand == "":
            return ""

        # Strip off the trailing parenthesis from the command and split into the function name and parameters
        pCommandComponents = sCommand.strip(")").split("(")
        sFunctionName = pCommandComponents[0]

        # Make sure the function name exists on either the unit operations wrapper, the sequence manager or the hardware layer
        if hasattr(UnitOperationsWrapper, sFunctionName):
            bUnitOperationsWrapper = True
            Object = UnitOperationsWrapper
            pObject = pUnitOperationsWrapper
        elif hasattr(HardwareComm, sFunctionName):
            bUnitOperationsWrapper = False
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
            pReturn = pFunction(pObject)
        elif nParameters == 1:
            pReturn = pFunction(pObject, pParameters[0])
        elif nParameters == 2:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1])
        elif nParameters == 3:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2])
        elif nParameters == 4:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3])
        elif nParameters == 5:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4])
        elif nParameters == 6:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4], pParameters[5])
        elif nParameters == 7:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4], pParameters[5], pParameters[6])
        else:
            raise Exception("Too many arguments");
        
        # Handle result
        if bUnitOperationsWrapper:
            # Remember the unit operation objects
            pSystemModel.SetUnitOperation(pReturn)
        elif pReturn != None:
            # Display results
            return str(pReturn)

        # Return success
        return ""      
    except Exception as ex:
        # Display the error
        return "Failed to execute command: " + str(ex)

# SendCommand implementation
def SendCommandImpl(sCommand, pHardware):
    """Parses and sends the raw command"""
    pCommandComponents = sCommand.split(" ")
    self.pHardwareComm._HardwareComm__SendRawCommand(pCommandComponents[1])

# GetState implementation
def GetStateImpl(pSystemModel):
    """Formats the state as a string"""
    return pSystemModel.DumpStateToString()

# AbortUnitOperation implementation
def AbortUnitOperationImpl(pSystemModel):
    """Abort the current unit operation"""
    # Get the current unit operation
    pCurrentUnitOperation = pSystemModel.GetUnitOperation()
    if pCurrentUnitOperation != None:
        # Abort the current unit operation
        pCurrentUnitOperation.abort = True
        return ""
    else:
        return "No current unit operation"

# DeliverUserInput implementation
def DeliverUserInputImpl(pSystemModel):
    """Delivers user input to the current unit operation"""
    # Get the current unit operation
    pCurrentUnitOperation = pSystemModel.GetUnitOperation()
    if pCurrentUnitOperation != None:
        # Deliver user input to the current user operation
        pCurrentUnitOperation.deliverUserInput()
        return ""
    else:
        return "No current unit operation"

# Base CLI class
class BaseCLI(threading.Thread):
    def ExecuteCommand(self, sCommand):
        """Parses and executes the given command"""
        raise Exception("Subclasses must implement ExecuteCommand")

    def SendCommand(self, sCommand):
        """Parses and sends the raw command"""
        raise Exception("Subclasses must implement SendCommand")

    def GetState(self):
        """Formats the state as a string"""
        raise Exception("Subclasses must implement GetState")

    def AbortUnitOperation(self):
        """Abort the current unit operation"""
        raise Exception("Subclasses must implement AbortUnitOperation")

    def DeliverUserInput(self):
        """Deliver user input to the current unit operation"""
        raise Exception("Subclasses must implement DeliverUserInput")

    def OpenScript(self, sCommand):
        """Opens the script"""
        # Strip off the trailing parenthesis from the command and split into the function name and script parameter
        pCommandComponents = sCommand.strip(")").split("(")
        sFunctionName = pCommandComponents[0]
        sScriptName = pCommandComponents[1]
    
        # Open and parse the file
        pScriptFile = open(sScriptName)
        return pScriptFile.readlines()

    def CleanCommand(self, sCommand):
        """Clean the input command"""
        nComment = sCommand.find("//")
        if nComment != -1:
            sCommand = sCommand[:nComment]
            sCommand = sCommand.strip()
        return sCommand

    def Run(self):
        """Main CLI function"""
        print "Elixys Command Line Interface"
        print "Type help for available commands."
        pScriptSteps = []
        bRunningScript = False
        nScriptStep = 0
        while True:
            # Prepare script prompt
            pScriptCommands = []
            if bRunningScript:
                # Check for end of script
                if nScriptStep >= len(pScriptSteps):
                    bRunningScript = False
                    print "Script complete"
                    sPrompt = ">>> "
                else:
                    # Get the next script commands
                    nCommandCount = 0
                    while bRunningScript:
                        # Stop if we are out of commands
                        if (nScriptStep + nCommandCount) == len(pScriptSteps):
                            break
                    
                        # Get the next command and append it to our array
                        sNextCommand = pScriptSteps[nScriptStep + nCommandCount].strip("\r\n")
                        pScriptCommands.append(sNextCommand)
                
                        # Clean off any comments and whitespace
                        sNextCommand = self.CleanCommand(sNextCommand)
                        if sNextCommand != "":
                            break
                        nCommandCount += 1
                    sPrompt = "Next step:" + "\n"
                    for sCommand in pScriptCommands:
                        if sCommand != "":
                            sPrompt += "  " + sCommand + "\n"
                    sPrompt += ">>> "
            else:
                # We're not running a script
                sPrompt = ">>> "

            # Get input and strip newlines
            sCommand = raw_input(sPrompt).strip("\r\n")

            # Handle commands
            if sCommand == "exit":
                break
            elif sCommand == "help":
                print "Recognized commands:"
                print "  help unit operations   Lists available unit operation functions"
                print "  help hardware          Lists available hardware functions"
                print "  help script            List available script functions"
                print "  help send              Display a brief description of the PLC command format" 
                print "  get state              Displays the current state of the system"
                print "  send [command]         Send the raw command to the PLC"
            elif sCommand == "help unit operations":
                # List the recognized unit operations
                print "Recognized unit operations:"
                print "  Init"
                print "  React"
                print "  Move"
                print "  Add"
                print "  Evaporate"
                print "  Install"
                print "  DeliverF18"
                print "  Transfer"
                print "  TransferToHPLC"
                print "  TempProfile"
                print "  RampPressure"
                print "  Mix"
                print "For additional information on each operation:"
                print "  help [unit operation name]"
                print "To abort the currently unit operation:"
                print "  AbortUnitOperation()"
                print "To deliver user input to a waiting unit operation:"
                print "  DeliverUserInput()"
            elif sCommand == "help Init":
                # React unit operation
                print "Initialize the Elixys hardware for use."
                print ""
                print "  Init()"
            elif sCommand == "help React":
                # React unit operation
                print "Heat the given reactor to a specific temperature, holds for a set length of"
                print "time, cools the reactor to the final temperature, stirs throughout."
                print ""
                print "  React(sReactor,                 'Reactor1','Reactor2','Reactor3'"
                print "        nReactionTemperature,     Celsius"
                print "        nReactionTime,            Seconds"
                print "        nFinalTemperature,        Celsius"
                print "        sReactPosition,           'React1','React2'"
                print "        nStirSpeed)               Suggested 500"
            elif sCommand == "help Move":
                # React unit operation
                print "Move the reactor to position specified."
                print ""
                print "  Move(sReactor,                 'Reactor1','Reactor2','Reactor3'"
                print "       sPosition)                'Add','Install','Evaporate','React1',"
                print "                                 'React2','Transfer'"
            elif sCommand == "help Add":
                # Add unit operation
                print "Adds the specified reagent to the reactor"
                print ""
                print "  Add(sReactor,                   Reactor where the reagent will be"
                print "                                  added ('Reactor1','Reactor2','Reactor3')"
                print "      nReagentReactor,            Reactor of the cassette where the reagent"
                print "                                  resides ('Reactor1','Reactor2','Reactor3')"
                print "      nReagentPosition,           1-11"
                print "      nReagentDeliveryPosition)   1 or 2"
            elif sCommand == "help Evaporate":
                # Evaporate unit operation
                print "Evaporates the contents of a reactor using a combination of heating, "
                print "stirring, nitrogen flow and vacuum."
                print ""
                print "  Evaporate(sReactor,                 'Reactor1','Reactor2','Reactor3'"
                print "            nEvaporationTemperature,  Celsius"
                print "            nEvaporationTime,         Seconds"
                print "            nFinalTemperature,        Celsius"
                print "            nStirSpeed)               Suggested 500"
            elif sCommand == "help Install":
                # Install unit operation
                print "Moves a reactor to the install position"
                print ""
                print "  Install(sReactor)               'Reactor1','Reactor2','Reactor3'"
            elif sCommand == "help DeliverF18":
                # Install unit operation
                print "Delivers F18 to Reactor 1 through a cartridge"
                print ""
                print "  DeliverF18(nTrapTime,         Seconds"
                print "             nTrapPressure,     PSI"
                print "             nEluteTime,        Seconds"
                print "             nElutePressure,    PSI"
                print "             nReagentReactor,   Reactor of the cassette where the reagent"
                print "                                resides ('Reactor1','Reactor2','Reactor3')"
                print "             nReagentPosition,  1-11"
                print "             bCyclotronFlag)    1 for cyclotron push, 0 for Elixys push"
            elif sCommand == "help Transfer":
                # Transfer unit operation
                print "Transfer the contents of one reactor to another through a cartridge"
                print ""
                print "  Transfer(sSourceReactor,      'Reactor1','Reactor2','Reactor3'"
                print "           sTargetReactor,      'Reactor1','Reactor2','Reactor3'"
                print "           sTransferType,       'Trap' or 'Elute'"
                print "           nTransferTime,       Seconds"
                print "           nTransferPressure)   PSI"
            elif sCommand == "help TransferToHPLC":
                # TransferToHPLC unit operation
                print "To do:  TransferToHPLC(nReactor, nStopcockPosition)"
            elif sCommand == "help TempProfile":
                # React unit operation
                print "Heats the reactor in the transfer position for temperature profiling."
                print ""
                print " TempProfile(sReactor,           'Reactor1','Reactor2','Reactor3'"
                print "             nProfileTemp,       Celsius"
                print "             nProfileTime,       Seconds"
                print "             nFinalTemperature,  Celsius"
                print "             nLiquidTCReactor,   Reactor of the liquid thermocouple"
                print "             nLiquidTCCollet)    Collet of the liquid thermocouple"
            elif sCommand == "help RampPressure":
                # Ramp pressure unit operation
                print "Ramps the pressure of one of the pressure regulators over a period of time"
                print ""
                print "  RampPressure(nPressureRegulator,      1 or 2"
                print "               nTargetPressure,         PSI"
                print "               nDuration)               Seconds"
            elif sCommand == "help Mix":
                # Mix unit operation
                print "Mixes the contents of the given reactor"
                print ""
                print "  Mix(sReactor,             'Reactor1','Reactor2','Reactor3'"
                print "      nStirSpeed,           Suggested 500"
                print "      nDuration)            Seconds"
            elif sCommand == "AbortUnitOperation()":
                # Abort the current unit operation
                self.AbortUnitOperation()
            elif sCommand == "DeliverUserInput()":
                # Deliver user input to the current unit operation
                self.DeliverUserInput()
            elif sCommand == "help hardware":
                # Yes, it's a wall of text.  We could use introspection for the function names but it gets even messier that way because we
                # don't want to list all of our functions
                print "Recognized hardware functions:"
                print "  * CoolingSystemOn()   * CoolingSystemOff()"
                print "  * VacuumSystemOn()    * VacuumSystemOff()"
                print "  * SetPressureRegulator(nPressureRegulator, nPressure)"
                print "  * MoveRobotToElute(nReactor)      MoveRobotToReagent(nReactor, nReagent)"
                print "  * MoveRobotToDelivery(nReactor, nPosition)"
                print "  * GripperUp()         * GripperDown()    * GripperOpen()   * GripperClose()"
                print "  * GasTransferUp()     * GasTransferDown()"
                print "  * GasTransferStart()  * GasTransferStop()"
                print "  * LoadF18Start()      * LoadF18Stop()    * LoadHPLCStart() * LoadHPLCStop()  "
                print "  * MoveReactor(nReactor, sPositionName)"
                print "  * ReactorUp(nReactor) * ReactorDown(nReactor)"
                print "  * ReactorStopcockCW(nReactor, nStopcock)"
                print "  * ReactorStopcockCCW(nReactor, nStopcock)"
                print "  * HeaterOn(nReactor)  * HeaterOff(nReactor)"
                print "  * SingleHeaterOn(nReactor, nCollet)   * SingleHeaterOff(nReactor, nCollet)"
                print "  * SetHeaterTemp(nReactor, fSetPoint)  * SetMotorSpeed(nReactor, nMotorSpeed)"
                print "  * HomeRobots()        * HomeReagentRobots()"
                print "  * HomeReactorRobots() * HomeReactorRobot(nReactor)"
                print "  * HomeReagentRobotX() * HomeReagentRobotY()  "
                print "  * DisableRobots()     * EnableRobots()"
                print "  * DisableReagentRobots()          * EnableReagentRobots()"
                print "  * DisableReactorRobot(nReactor)   * EnableReactorRobot(nReactor)"
                print "All values are numbers except sPositionName which is one of the following:"
                print "      Install, Transfer, React1, Add, React2, Evaporate, Radiation"
            elif sCommand == "help script":
                # List the available script functions
                print "Recognized script functions:"
                print "  OpenScript(sFilename)"
                print "  CloseScript()"
                print "  RestartScript()"
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
                print self.GetState()
            elif sCommand.startswith("send "):
                # Attempt to send the command
                self.SendCommand(sCommand)

                # Sleep a bit to give the PLC a chance to response before we display the input prompt
                time.sleep(0.25)
            elif sCommand.startswith("OpenScript"):
                # Open the script
                pScriptSteps = self.OpenScript(sCommand)
                bRunningScript = True
                nScriptStep = 0
            elif sCommand.startswith("CloseScript"):
                # Close the script
                pScriptSteps = []
                bRunningScript = False
                nScriptStep = 0
            elif sCommand.startswith("RestartScript"):
                # Restart the script
                bRunningScript = True
                nScriptStep = 0
            else:
                # Are we running a script and executing the next command?
                if bRunningScript and (sCommand == ""):
                    # Yes, so execute each valid command
                    print "Executing step: "
                    for sNextCommand in pScriptCommands:
                        sNextCommand = self.CleanCommand(sNextCommand)
                        if sNextCommand != "":
                            print "  " + sNextCommand
                            self.ExecuteCommand(sNextCommand)

                    # Update our step number
                    nScriptStep += len(pScriptCommands)
                else:
                    # No, so attempt to execute the command
                    self.ExecuteCommand(sCommand)

                    # Sleep a bit to give the PLC a chance to response before we display the input prompt
                    time.sleep(0.1)

