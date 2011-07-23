""" ElixysHardwareComm.py

Implements the HardwareComm interface for the Elixys hardware """

### Imports ###
from configobj import ConfigObj
from SocketThread import SocketThread
import threading
import time

### Constants ###

# IP and port of the PLC.  Make sure only one PLC IP is defined
#PLC_IP = "192.168.1.200"    # Real PLC
PLC_IP = "127.0.0.1"        # Fake PLC for testing and demo
PLC_PORT = 9600

# Number of words used by each type of module
DIGITALOUT_SIZE = 0x4
DIGITALIN_SIZE = 0x1
ANALOGOUT_SIZE = 0xa
ANALOGIN_SIZE = 0xa
THERMOCONTROLLER_SIZE = 0x14
DEVICENET_SIZE = 0x19

# RoboNet constants
ROBONET_MIN = 3201
ROBONET_MAX = 3309 + (5 * 4)
ROBONET_ENABLE = 3201
ROBONET_CONTROL = 3212
ROBONET_AXISPOSSET = 3209
ROBONET_AXISPOSREAD = 3309
ROBONET_SUCCESS = 0x7013
ROBONET_ERROR = 0x700a

# Constants for PLC command formatting
MAX_PLC_READLENGTH = 0x350
ICF = "80"    #Info Ctrl Field - Binary 80 or 81 [1][0=Cmd 1=Resp][00000][0 or 1=Resp Req]                      
RSV = "00"    #Reserved - Always Zero
GCT = "02"    #Gateway Count - Set to 02 (or do not set?!)
DNET = "00"   #Dest. Network - 00 (Local Network)
DNODE = "C8"  #Dest. Node - Ethernet IP?
DUNIT = "00"  #Dest. Unit - 00=CPU FE=Ethernet
SNET = "00"   #Src. Net - 00 (Local Network)
SNODE = "02"  #Src. Node
SUNIT = "00"  #Src. Unit - 00=CPU
SVCID = "00"  #Service ID - 
PACKETINFO = [ICF,RSV,GCT,DNET,DNODE,DUNIT,SNET,SNODE,SUNIT,SVCID]
FINSHEADER = ["46","49","4E","53"]
FINSCLOSING = ["05", "01"]
PLCCOMMANDS = {"0101":"MEMORY AREA READ",
    "0102":"MEMORY AREA WRITE",
    "0103":"MEMORY AREA FILL",
    "0104":"MULTIPLE MEMORY AREA READ",
    "0105":"MEMORY AREA TRANSFER",
    "0201":"PARAMETER AREA READ",
    "0202":"PARAMETER AREA WRITE",
    "0203":"PARAMETER AREA CLEAR",
    "0306":"PROGRAM AREA READ",
    "0307":"PROGRAM AREA WRITE",
    "0308":"PROGRAM AREA CLEAR",
    "0401":"RUN",
    "0402":"STOP",
    "0501":"CPU UNIT DATA READ",
    "0502":"CONNECTION DATA READ",
    "0601":"CPU UNIT STATUS READ",
    "0620":"CYCLE TIME READ",
    "0701":"CLOCK READ",
    "0702":"CLOCK WRITE",
    "0920":"MESSAGE CLEAR",
    "0C01":"ACCESS RIGHT ACQUIRE",
    "0C02":"ACCESS RIGHT FORCED ACQUIRE",
    "0C03":"ACCESS RIGHT RELEASE",
    "2101":"ERROR CLEAR",
    "2102":"ERROR LOG READ",
    "2103":"ERROR LOG CLEAR",
    "2140":"FINS WRITE ACCESS LOG READ",
    "2141":"FINS WRITE ACCESS LOG CLEAR",
    "2201":"FILE NAME READ",
    "2202":"SINGLE FILE READ",
    "2203":"SINGLE FILE WRITE",
    "2204":"FILE MEMORY FORMAT",
    "2205":"FILE DELETE",
    "2207":"FILE COPY",
    "2208":"FILE NAME CHANGE",
    "220A":"MEMORY AREA FILE TRANSFER",
    "220B":"PARAMETER AREA FILE TRANS",
    "220C":"PROGRAM AREA FILE TRANSF",
    "2215":"CREATE/DELETE DIRECTORY",
    "2220":"MEMORY CASSETTE TRANSFER",
    "2301":"FORCED SET/RESET ",
    "2302":"FORCED SET/RESET CANCEL"}
PLCERRORS = {"0001":"Local node not in network",
    "0102":"Token timed out",
    "0103":"Retries failed",
    "0104":"Too many send frames",
    "0105":"Node address out of range",
    "0106":"Duplicate node address",
    "0201":"Destination node not in network",
    "0202":"Unit missing",
    "0203":"Third node missing",
    "0204":"Destination node busy",
    "0205":"Response timeout",
    "0301":"Communications controller error",
    "0302":"CPU unit error",
    "0303":"Controller error",
    "0304":"Unit number error",
    "0401":"Undefined command",
    "0402":"Not supported by model/version",
    "0501":"Destination setting address error",
    "0502":"No routing tables",
    "0503":"Routing table error",
    "0504":"Too many relays",
    "1001":"Command too long",
    "1002":"Command too short",
    "1003":"Elements/data don't match",
    "1004":"Command format error",
    "1005":"Header error",
    "1101":"Area classification missing",
    "1102":"Access size error",
    "1103":"Address range error",
    "1104":"Address range exceeded",
    "1106":"Program missing",
    "1109":"Relational error",
    "110A":"Duplicate data access",
    "110B":"Response too long",
    "110C":"Parameter error",
    "2002":"Protected",
    "2003":"Table missing",
    "2004":"Data missing",
    "2005":"Program missing",
    "2006":"File missing",
    "2007":"Data mismatch",
    "2101":"Read only",
    "2102":"Protected",
    "2103":"Cannot register",
    "2105":"Program missing",
    "2106":"File missing",
    "2107":"File already exists",
    "2108":"Cannot change"}

# HardwareComm class implementation for the Elixys system
class HardwareComm():

    ### Construction ###
    def __init__(self):
        # Load the hardware map and robot positions
        self.__pHardwareMap = ConfigObj("../hardware/HardwareMap.ini")
        self.__pRobotPositions = ConfigObj("../hardware/RobotPositions.ini")

        # Extract the module offsets and units
        self.__nAnalogOutUnit = int(self.__pHardwareMap["AnalogOutUnit"], 16)
        self.__nAnalogInUnit = int(self.__pHardwareMap["AnalogInUnit"], 16)
        self.__nThermocontroller1Unit = int(self.__pHardwareMap["Thermocontroller1Unit"], 16)
        self.__nThermocontroller2Unit = int(self.__pHardwareMap["Thermocontroller2Unit"], 16)
        self.__nThermocontroller3Unit = int(self.__pHardwareMap["Thermocontroller3Unit"], 16)
        self.__nDeviceNetOffset = int(self.__pHardwareMap["DeviceNetUnit"], 16)
        self.__nDigitalOutOffset = int(self.__pHardwareMap["DigitalOutOffset"], 16)
        self.__nDigitalInOffset = int(self.__pHardwareMap["DigitalInOffset"], 16)

        # Load conversion constants
        self.__nPressureRegulatorSetSlope = float(self.__pHardwareMap["PressureRegulatorSetSlope"])
        self.__nPressureRegulatorSetIntercept = float(self.__pHardwareMap["PressureRegulatorSetIntercept"])
        self.__nPressureRegulatorActualSlope = float(self.__pHardwareMap["PressureRegulatorActualSlope"])
        self.__nPressureRegulatorActualIntercept = float(self.__pHardwareMap["PressureRegulatorActualIntercept"])
        self.__nVacuumGaugeSlope = float(self.__pHardwareMap["VacuumGaugeSlope"])
        self.__nVacuumGaugeIntercept = float(self.__pHardwareMap["VacuumGaugeIntercept"])

        # Load the motor axes
        self.__nReagentXAxis = int(self.__pRobotPositions["ReagentXAxis"])
        self.__nReagentZAxis = int(self.__pRobotPositions["ReagentZAxis"])
        self.__nReactor1Axis = int(self.__pRobotPositions["Reactor1Axis"])
        self.__nReactor2Axis = int(self.__pRobotPositions["Reactor2Axis"])
        self.__nReactor3Axis = int(self.__pRobotPositions["Reactor3Axis"])

        # Load the reactor offsets
        self.__nReactor1CassetteXOffset = int(self.__pRobotPositions["Reactor1"]["CassetteXOffset"])
        self.__nReactor1CassetteZOffset = int(self.__pRobotPositions["Reactor1"]["CassetteZOffset"])
        self.__nReactor1ReactorOffset = int(self.__pRobotPositions["Reactor1"]["ReactorOffset"])
        self.__nReactor2CassetteXOffset = int(self.__pRobotPositions["Reactor2"]["CassetteXOffset"])
        self.__nReactor2CassetteZOffset = int(self.__pRobotPositions["Reactor2"]["CassetteZOffset"])
        self.__nReactor2ReactorOffset = int(self.__pRobotPositions["Reactor2"]["ReactorOffset"])
        self.__nReactor3CassetteXOffset = int(self.__pRobotPositions["Reactor3"]["CassetteXOffset"])
        self.__nReactor3CassetteZOffset = int(self.__pRobotPositions["Reactor3"]["CassetteZOffset"])
        self.__nReactor3ReactorOffset = int(self.__pRobotPositions["Reactor3"]["ReactorOffset"])

        # Calculate the memory address range.  We will use this information to query for the entire state at once
        self.__nMemoryLower, self.__nMemoryUpper = self.__CalculateMemoryRange()

        # Initialize our variables
        self.__bUpdatingState = False
        self.__pSystemModel = None
        
    ### Public functions ###

    # Startup
    def StartUp(self, bResetSystem = True):
        # Spawn the socket thread
        self.__pSocketThread = SocketThread()
        self.__pSocketThreadTerminateEvent = threading.Event()
        self.__pSocketThread.SetParameters(PLC_IP, PLC_PORT, self, self.__pSocketThreadTerminateEvent)
        self.__pSocketThread.start()
        
        # Enable analog out
        self.__SetIntegerValueRaw(2000, 255);
        
        # Enable RoboNet control for all axes
        self.__SetIntegerValueRaw(ROBONET_ENABLE, 0x8000)

    # Shutdown               
    def ShutDown(self):
        # Stop the socket thread
        self.__pSocketThreadTerminateEvent.set()
        self.__pSocketThread.join()

    # Set the system model
    def SetSystemModel(self, pSystemModel):
        self.__pSystemModel = pSystemModel
        
    # Update state
    def UpdateState(self):
        # Make sure we're not already in the process of updating the state
        if self.__bUpdatingState == True:
            return
            
        # We're limited in the maximum amount of data we can read in a single request.  Start by requesting the
        # first chunk of the state
        self.__bUpdatingState = True
        self.__nStateOffset = self.__nMemoryLower
        self.__sState = ""
        self.__RequestNextStateChunk()

    # Vacuum system
    def VacuumSystemOn(self):
        self.__SetBinaryValue("VacuumSystemOn", True)
    def VacuumSystemOff(self):
        self.__SetBinaryValue("VacuumSystemOn", False)

    # Cooling system
    def CoolingSystemOn(self):
        self.__SetBinaryValue("CoolingSystemOn", True)
    def CoolingSystemOff(self):
        self.__SetBinaryValue("CoolingSystemOn", False)

    # Pressure regulator
    def SetPressureRegulator(self, nPressureRegulator, nPressurePSI):
        nPressurePLC = (nPressurePSI * self.__nPressureRegulatorSetSlope) + self.__nPressureRegulatorSetIntercept
        if nPressurePLC < 0:
            nPressurePLC = 0
        self.__SetAnalogValue("PressureRegulator" + str(nPressureRegulator) + "_SetPressure", nPressurePLC)

    # Reagent robot
    def MoveRobotToReagent(self, nReactor, nReagent):
        pPosition = self.__LookUpRobotPosition("ReagentRobot_Reagent" + str(nReagent))
        self.__SetRobotPosition(self.__nReagentXAxis, self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"]))
        self.__SetRobotPosition(self.__nReagentZAxis, self.__LookUpReactorCassetteZOffset(nReactor) + int(pPosition["z"]))
    def MoveRobotToDelivery(self, nReactor, nPosition):
        pPosition = self.__LookUpRobotPosition("ReagentRobot_ReagentDelivery" + str(nPosition))
        self.__SetRobotPosition(self.__nReagentXAxis, self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"]))
        self.__SetRobotPosition(self.__nReagentZAxis, self.__LookUpReactorCassetteZOffset(nReactor) + int(pPosition["z"]))
    def GripperUp(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperDown", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", True)
    def GripperDown(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperDown", True)
    def GripperOpen(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperClose", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", True)
    def GripperClose(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperClose", True)

    # F-18
    def LoadF18Start(self):
        self.__SetBinaryValue("F18_Load", True)
    def LoadF18Stop(self):
        self.__SetBinaryValue("F18_Load", False)
    def EluteF18Start(self):
        self.__SetBinaryValue("F18_Elute", True)
    def EluteF18Stop(self):
        self.__SetBinaryValue("F18_Elute", False)

    # HPLC
    def LoadHPLCStart(self):
        self.__SetBinaryValue("HPLC_Load", True)
    def LoadHPLCStop(self):
        self.__SetBinaryValue("HPLC_Load", False)

    # Reactor
    def MoveReactor(self, nReactor, sPositionName):
        if (nReactor == 1):
            nReactorOffset = self.__nReactor1ReactorOffset
        elif (nReactor == 2):
            nReactorOffset = self.__nReactor2ReactorOffset
        elif (nReactor == 3):
            nReactorOffset = self.__nReactor3ReactorOffset
        else:
            raise Exception("Invalid reactor")
        pPosition = self.__LookUpRobotPosition("Reactors_" + sPositionName)
        self.__SetRobotPosition(self.__LookUpReactorAxis(nReactor), nReactorOffset + int(pPosition["z"]))
    def ReactorUp(self, nReactor):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorDown", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorUp", True)
    def ReactorDown(self, nReactor):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorUp", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorDown", True)
    def ReactorEvaporateStart(self, nReactor):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_EvaporationNitrogenValve", True)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_EvaporationVacuumValve", True)
    def ReactorEvaporateStop(self, nReactor):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_EvaporationNitrogenValve", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_EvaporationVacuumValve", False)
    def ReactorTransferStart(self, nReactor):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_TransferValve", True)
    def ReactorTransferStop(self, nReactor):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_TransferValve", False)
    def ReactorReagentTransferStart(self, nReactor, nPosition):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Reagent" + str(nPosition) + "TransferValve", True)
    def ReactorReagentTransferStop(self, nReactor, nPosition):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Reagent" + str(nPosition) + "TransferValve", False)
    def ReactorStopcockOpen(self, nReactor, nStopcock):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValveClose", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValveOpen", True)
    def ReactorStopcockClose(self, nReactor, nStopcock):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValveOpen", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValveClose", True)

    # Temperature controllers
    def HeaterOn(self, nReactor, nHeater):
        # Clear the stop bit
        nWordOffset, nBitOffset = self.__LoopUpHeaterStop(nReactor, nHeater)
        self.__SetBinaryValueRaw(nWordOffset, nBitOffset, 0)
    def HeaterOff(self, nReactor, nHeater):
        # Set the stop bit
        nWordOffset, nBitOffset = self.__LoopUpHeaterStop(nReactor, nHeater)
        self.__SetBinaryValueRaw(nWordOffset, nBitOffset, 1)
    def SetHeater(self, nReactor, nHeater, nSetPoint):
        # Set the heater temperature
        self.__SetThermocontrollerSetValue("Reactor" + str(nReactor) + "_TemperatureController" + str(nHeater), nSetPoint)

    # Stir motor
    def SetMotorSpeed(self, nReactor, nMotorSpeed):
        self.__SetAnalogValue("Reactor" + str(nReactor) + "_StirMotor", nMotorSpeed)

    # Radiation detector
    def UpdateRadiationDetector(self, nReactor):
        pass

    # Home all robots
    def HomeRobots(self):
        print "Homing all axes"
        for nAxis in range(0, 5):
            self.__SetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4), 0x10)                # Turn on servo axis
        time.sleep(0.1)
        for nAxis in range(0, 5):
            self.__SetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4), 0x12)                # Home axis

    # Disable all robots
    def DisableRobots(self):
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 0, 0x08)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 4, 0x08)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 8, 0x08)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 12, 0x08)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 16, 0x08)
        
    # Enable all robots
    def EnableRobots(self):
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 0, 0x10)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 4, 0x10)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 8, 0x10)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 12, 0x10)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + 16, 0x10)

    # Disable reactor robot
    def DisableReactorRobot(self, nReactor):
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__LookUpReactorAxis(nReactor) * 4), 0x08)

    # Enable reactor robot
    def EnableReactorRobot(self, nReactor):
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__LookUpReactorAxis(nReactor) * 4), 0x10)

    # Temporary hack: this is how we log the temperature when generating a heating and cooling profile
    def SetStateCallback(self, fStateCallback):
        self.__fStateCallback = fStateCallback

    ### PLC send functions ###

    # Set binary value
    def __SetBinaryValue(self, sHardwareName, bValue):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calcuate the absolute address of the target bit
        nRelativeBitOffset = int(pHardware["location"])
        nBitOffset = nRelativeBitOffset % 0x10
        nWordOffset = self.__DetermineHardwareOffset(pHardware) + ((nRelativeBitOffset - nBitOffset) / 0x10)

        # Set the binary value
        self.__SetBinaryValueRaw(nWordOffset, nBitOffset, bValue)
        
    # Set binary value raw
    def __SetBinaryValueRaw(self, nWordOffset, nBitOffset, bValue):
        # Format and send the raw command
        sCommand = "010230"					            # Write bit to CIO memory
        sCommand = sCommand + ("%0.4X" % nWordOffset)	# Memory offset (words)
        sCommand = sCommand + ("%0.2X" % nBitOffset)    # Memory offset (bits)
        sCommand = sCommand + "0001"				    # Number of bits to write
        if bValue:
            sCommand = sCommand + "01"				    # Set bit
        else:
            sCommand = sCommand + "00"				    # Clear bit
        self.__SendRawCommand(sCommand)

    # Set integer value by hardware name
    def __SetIntegerValue(self, sHardwareName, nValue):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Call the raw function
        self.__SetIntegerValueRaw(int(pHardware["location"]), nValue)

    # Set integer value raw
    def __SetIntegerValueRaw(self, nAddress, nValue):
        # Format and send the raw command
        sCommand = "0102B0"					                    # Write word to CIO memory
        sCommand = sCommand + ("%0.4X" % nAddress)              # Memory offset (words)
        sCommand = sCommand + "00"                              # Memory offset (bits)
        sCommand = sCommand + "0001"				            # Number of bits to write
        sCommand = sCommand + ("%0.4X" % nValue)				# Set bit
        self.__SendRawCommand(sCommand)

    # Set analog value
    def __SetAnalogValue(self, sHardwareName, nValue):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calculate the absolute address of the target word
        nAbsoluteWordOffset = self.__DetermineHardwareOffset(pHardware) +  int(pHardware["location"])
        
        # Set the integer value
        self.__SetIntegerValueRaw(nAbsoluteWordOffset, nValue)

    # Set thermocontroller value
    def __SetThermocontrollerSetValue(self, sHardwareName, nValue):
        # Look up the temperature set offset and set the value
        nOffset = self.__LookUpThermocontrollerSetOffset(sHardwareName)
        self.__SetIntegerValueRaw(nOffset, nValue)

    # Move robot to position
    def __SetRobotPosition(self, nAxis, nPosition):
        # Move motor
        self.__SetIntegerValueRaw(ROBONET_AXISPOSSET + (nAxis * 4), nPosition)   # Set axis position
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4), 0x11)           # Move to position
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4), 0x10)           # Clear axis home bit

    ### PLC raw message functions ###
    
    # Sends a raw command to the PLC
    def __SendRawCommand(self, sCommand):
        try:
            # Make sure the command is an even number of characters so we can interpret it as a hex string
            if (len(sCommand) % 2) != 0:
                raise Exception("Invalid packet length")

            # Construct a packet from the command
            pPacketList = []
            pPacketList.extend(PACKETINFO)
            pPacketList.extend(sCommand)
            sPacket = ""
            for item in pPacketList:
                sPacket += item
            sBinaryPacket = sPacket.decode("hex")

            # Send the packet
            self.__pSocketThread.SendPacket(sBinaryPacket)
        except Exception as ex:
            # Display the error
            print "Failed to send packet to PLC (" + str(ex) + ")"

    # Processes a raw response from the PLC
    def __ProcessRawResponse(self, sResponse):
        # Strip the header info off the response and check for errors
        sResponse = sResponse[20:]
        sError = sResponse[4:8]
        if sError != "0000":
            # Error encountered
            if sError in PLCERRORS:
                raise Exception("PLC error: " + PLCERRORS[sError])
            else:
                raise Exception("PLC error: " + sError)

        # Ignore responses that are too short
        if len(sResponse) <= 8:
            return

        # Check the response type
        if sResponse[:4] == "0101":
            # This read response should contain the system state
            self.__ProcessRawState(sResponse[8:])
        elif sResponse[:4] == "0501":
            # Handle unit info message response
            sResponse = sResponse[8:]
            print ("CPU Unit Model: %s" % sResponse[:40].decode("hex"))
            print ("CPU Version: v%s" % sResponse[40:60].decode("hex"))
            print ("Internal CPU Version: v%s" % sResponse[60:80].decode("hex"))
            print ("DIP Switch: %s" % int(sResponse[80:82],16))
            print ("Largest EM Bank #: Bank %s" % int(sResponse[82:84],16)) #Next 36(72) are reserved
            print ("Program Area Size: %sKb" % int(sResponse[160:164],16))
            print ("IOM Size: %sKb" % int(sResponse[164:166],16)) #[108:120].decode("hex")
            print ("Number of DM Words: %s Words" % int(sResponse[166:170],16))
            print ("Timer/Counter Size: %s" % (int(sResponse[170:172],16)*1024))
            print ("EM Size: %sKb" % (int(sResponse[172:174],16)*32))
            print ("Memory Card Size: %s" % int(sResponse[178:180],16))
            print ("Memory Card Type: %s" % int(sResponse[180:184],16))
            print ("CPU Bus Config: %s" % sResponse[184:])
        else:
            # Just display the message for now
            print "Unknown response: " + sResponse

    ### State functions ###
    
    # Requests the next chunk of the state from the PLC
    def __RequestNextStateChunk(self):
        # Make sure we're updating our state
        if self.__bUpdatingState == False:
            return

        # Determine the length of the next chunk
        if (self.__nStateOffset + MAX_PLC_READLENGTH) < self.__nMemoryUpper:
            nLength = MAX_PLC_READLENGTH
        else:
            nLength = self.__nMemoryUpper - self.__nStateOffset
        
        # Fetch the next chunk of the state
        sCommand = "0101B0"                           # Read words from CIO memory
        sCommand += ("%0.4X" % self.__nStateOffset)   # Memory offset (words)
        sCommand += "00"                              # Memory offset (bits)
        sCommand += ("%0.4X" % nLength)               # Number of words to read
        self.__SendRawCommand(sCommand)

    # Process the raw state we've received from the PLC
    def __ProcessRawState(self, sState):
        # Append this chunk to our state
        self.__sState += sState
        self.__nStateOffset += len(sState) / 4
        
        # Do we have the entire state?
        if self.__nStateOffset < self.__nMemoryUpper:
            # No, so request the next chunk and return
            self.__RequestNextStateChunk()
            return
        else:
            # Yes, so clear our updating flag
            self.__bUpdatingState = False

        # Temporary hack: check if the callback function is defined
        try:
            self.__fStateCallback(self.__GetThermocontrollerActualValue("Reactor1_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor1_TemperatureController2"),
                self.__GetThermocontrollerActualValue("Reactor1_TemperatureController3"),
                self.__GetThermocontrollerActualValue("Reactor2_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor2_TemperatureController2"),
                self.__GetThermocontrollerActualValue("Reactor2_TemperatureController3"),
                self.__GetThermocontrollerActualValue("Reactor3_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor3_TemperatureController2"),
                self.__GetThermocontrollerActualValue("Reactor3_TemperatureController3"))
            return
        except AttributeError:
            pass

        # Format the state into a string for the moment
        sStateText = "Vacuum pressure: " + str(self.__GetVacuum()) + "\n"
        sStateText += "Cooling system on: " + str(self.__GetBinaryValue("CoolingSystemOn")) + "\n"
        sStateText += "Pressure regulator 1 set/actual: %.1f/%.1f\n"%(self.__GetPressureRegulatorSetPressure(1), self.__GetPressureRegulatorActualPressure(1))
        sStateText += "Pressure regulator 2 set/actual: %.1f/%.1f\n"%(self.__GetPressureRegulatorSetPressure(2), self.__GetPressureRegulatorActualPressure(2))
        sStateText += "Reagent robot:\n"
        sStateText += "  Position set/actual/status: (" + str(self.__GetReagentReactorSetX()) + ", " + str(self.__GetReagentReactorSetZ()) + ")/(" + \
            str(self.__GetReagentReactorActualX()) + ", " + str(self.__GetReagentReactorActualZ()) + ")/(" + \
            str(self.__GetRobotStatus(self.__nReagentXAxis)) + ", " + str(self.__GetRobotStatus(self.__nReagentZAxis)) + ")\n"
        sStateText += "  Gripper up set: " + str(self.__GetBinaryValue("ReagentRobot_SetGripperUp")) + "\n"
        sStateText += "  Gripper down set: " + str(self.__GetBinaryValue("ReagentRobot_SetGripperDown")) + "\n"
        sStateText += "  Gripper open set: " + str(self.__GetBinaryValue("ReagentRobot_SetGripperOpen")) + "\n"
        sStateText += "  Gripper close set: " + str(self.__GetBinaryValue("ReagentRobot_SetGripperClose")) + "\n"
        sStateText += "Reactor 1:\n"
        sStateText += "  Position set/actual/status: " + str(self.__GetReactorRobotSetPosition(1)) + "/" + \
            str(self.__GetReactorRobotActualPosition(1)) + "/" + str(self.__GetRobotStatus(self.__nReactor1Axis)) + "\n"
        sStateText += "  Reactor up set/actual: " + str(self.__GetBinaryValue("Reactor1_SetReactorUp")) + "/" + \
            str(self.__GetBinaryValue("Reactor1_ReactorUp")) + "\n"
        sStateText += "  Reactor down set/actual: " + str(self.__GetBinaryValue("Reactor1_SetReactorDown")) + "/" + \
            str(self.__GetBinaryValue("Reactor1_ReactorDown")) + "\n"
        sStateText += "  Evaporation valve open: " + str(self.__GetBinaryValue("Reactor1_EvaporationNitrogenValve")) + "\n"
        sStateText += "  Vacuum valve open: " + str(self.__GetBinaryValue("Reactor1_EvaporationVacuumValve")) + "\n"
        sStateText += "  Transfer valve open: " + str(self.__GetBinaryValue("Reactor1_TransferValve")) + "\n"
        sStateText += "  Reagent 1 transfer valve: " + str(self.__GetBinaryValue("Reactor1_Reagent1TransferValve")) + "\n"
        sStateText += "  Reagent 2 transfer valve: " + str(self.__GetBinaryValue("Reactor1_Reagent2TransferValve")) + "\n"
        sStateText += "  Stopcock 1 valve open/close: " + str(self.__GetBinaryValue("Reactor1_Stopcock1ValveOpen")) + "/" + \
            str(self.__GetBinaryValue("Reactor1_Stopcock1ValveClose")) + "\n"
        sStateText += "  Stopcock 2 valve open/close: " + str(self.__GetBinaryValue("Reactor1_Stopcock2ValveOpen")) + "/" + \
            str(self.__GetBinaryValue("Reactor1_Stopcock2ValveClose")) + "\n"
        sStateText += "  Stopcock 3 valve open/close: " + str(self.__GetBinaryValue("Reactor1_Stopcock3ValveOpen")) + "/" + \
            str(self.__GetBinaryValue("Reactor1_Stopcock3ValveClose")) + "\n"
        sStateText += "  Temperature controller 1 on/set/actual: " + str(self.__GetHeaterOn(1, 1)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor1_TemperatureController1")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor1_TemperatureController1")) + "\n"
        sStateText += "  Temperature controller 2 on/set/actual: " + str(self.__GetHeaterOn(1, 2)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor1_TemperatureController2")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor1_TemperatureController2")) + "\n"
        sStateText += "  Temperature controller 3 on/set/actual: " + str(self.__GetHeaterOn(1, 3)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor1_TemperatureController3")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor1_TemperatureController3")) + "\n"
        sStateText += "  Stir motor: " + str(self.__GetAnalogValue("Reactor1_StirMotor")) + "\n"
        sStateText += "  Radiation detector: TBD\n"
        sStateText += "Reactor 2:\n"
        sStateText += "  Position set/actual/status: " + str(self.__GetReactorRobotSetPosition(2)) + "/" + \
            str(self.__GetReactorRobotActualPosition(2)) + "/" + str(self.__GetRobotStatus(self.__nReactor2Axis)) + "\n"
        sStateText += "  Reactor up set/actual: " + str(self.__GetBinaryValue("Reactor2_SetReactorUp")) + "/" + \
            str(self.__GetBinaryValue("Reactor2_ReactorUp")) + "\n"
        sStateText += "  Reactor down set/actual: " + str(self.__GetBinaryValue("Reactor2_SetReactorDown")) + "/" + \
            str(self.__GetBinaryValue("Reactor2_ReactorDown")) + "\n"
        sStateText += "  Evaporation valve open: " + str(self.__GetBinaryValue("Reactor2_EvaporationNitrogenValve")) + "\n"
        sStateText += "  Vacuum valve open: " + str(self.__GetBinaryValue("Reactor2_EvaporationVacuumValve")) + "\n"
        sStateText += "  Transfer valve open: " + str(self.__GetBinaryValue("Reactor2_TransferValve")) + "\n"
        sStateText += "  Reagent 1 transfer valve: " + str(self.__GetBinaryValue("Reactor2_Reagent1TransferValve")) + "\n"
        sStateText += "  Reagent 2 transfer valve: " + str(self.__GetBinaryValue("Reactor2_Reagent2TransferValve")) + "\n"
        sStateText += "  Stopcock 1 valve open/close: " + str(self.__GetBinaryValue("Reactor2_Stopcock1ValveOpen")) + "/" + \
            str(self.__GetBinaryValue("Reactor2_Stopcock1ValveClose")) + "\n"
        sStateText += "  Temperature controller 1 on/set/actual: " + str(self.__GetHeaterOn(2, 1)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor2_TemperatureController1")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor2_TemperatureController1")) + "\n"
        sStateText += "  Temperature controller 2 on/set/actual: " + str(self.__GetHeaterOn(2, 2)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor2_TemperatureController2")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor2_TemperatureController2")) + "\n"
        sStateText += "  Temperature controller 3 on/set/actual: " + str(self.__GetHeaterOn(2, 3)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor2_TemperatureController3")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor2_TemperatureController3")) + "\n"
        sStateText += "  Stir motor: " + str(self.__GetAnalogValue("Reactor2_StirMotor")) + "\n"
        sStateText += "  Radiation detector: TBD\n"
        sStateText += "Reactor 3:\n"
        sStateText += "  Position set/actual/status: " + str(self.__GetReactorRobotSetPosition(3)) + "/" + \
            str(self.__GetReactorRobotActualPosition(3)) + "/" + str(self.__GetRobotStatus(self.__nReactor3Axis)) + "\n"
        sStateText += "  Reactor up set/actual: " + str(self.__GetBinaryValue("Reactor3_SetReactorUp")) + "/" + \
            str(self.__GetBinaryValue("Reactor3_ReactorUp")) + "\n"
        sStateText += "  Reactor down set/actual: " + str(self.__GetBinaryValue("Reactor3_SetReactorDown")) + "/" + \
            str(self.__GetBinaryValue("Reactor3_ReactorDown")) + "\n"
        sStateText += "  Evaporation valve open: " + str(self.__GetBinaryValue("Reactor3_EvaporationNitrogenValve")) + "\n"
        sStateText += "  Vacuum valve open: " + str(self.__GetBinaryValue("Reactor3_EvaporationVacuumValve")) + "\n"
        sStateText += "  Transfer valve open: " + str(self.__GetBinaryValue("Reactor3_TransferValve")) + "\n"
        sStateText += "  Reagent 1 transfer valve: " + str(self.__GetBinaryValue("Reactor3_Reagent1TransferValve")) + "\n"
        sStateText += "  Reagent 2 transfer valve: " + str(self.__GetBinaryValue("Reactor3_Reagent2TransferValve")) + "\n"
        sStateText += "  Stopcock 1 valve open/close: " + str(self.__GetBinaryValue("Reactor3_Stopcock1ValveOpen")) + "/" + \
            str(self.__GetBinaryValue("Reactor3_Stopcock1ValveClose")) + "\n"
        sStateText += "  Temperature controller 1 on/set/actual: " + str(self.__GetHeaterOn(3, 1)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor3_TemperatureController1")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor3_TemperatureController1")) + "\n"
        sStateText += "  Temperature controller 2 on/set/actual: " + str(self.__GetHeaterOn(3, 2)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor3_TemperatureController2")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor3_TemperatureController2")) + "\n"
        sStateText += "  Temperature controller 3 on/set/actual: " + str(self.__GetHeaterOn(3, 3)) + "/" + \
            str(self.__GetThermocontrollerSetValue("Reactor3_TemperatureController3")) + "/" + \
            str(self.__GetThermocontrollerActualValue("Reactor3_TemperatureController3")) + "\n"
        sStateText += "  Stir motor: " + str(self.__GetAnalogValue("Reactor3_StirMotor")) + "\n"
        sStateText += "  Radiation detector: TBD\n"
        print sStateText
        
    # Get binary value
    def __GetBinaryValue(self, sHardwareName):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calcuate the absolute address of the target bit
        nRelativeBitOffset = int(pHardware["location"])
        nBitOffset = nRelativeBitOffset % 0x10
        nWordOffset = self.__DetermineHardwareOffset(pHardware) + ((nRelativeBitOffset - nBitOffset) / 0x10)

        # Make sure the address is within range
        if (nWordOffset < self.__nMemoryLower) or (nWordOffset >= self.__nMemoryUpper):
            print "Offset out of range"
            return

        # Return the raw value
        return self.__GetBinaryValueRaw(nWordOffset, nBitOffset)

    # Get binary value raw
    def __GetBinaryValueRaw(self, nWordOffset, nBitOffset):
        # Extract the return the value
        sWord = self.__sState[((nWordOffset - self.__nMemoryLower) * 4):((nWordOffset - self.__nMemoryLower + 1) * 4)]
        nWord = int(sWord, 0x10)
        nBit = (nWord >> nBitOffset) & 1
        return nBit != 0

    # Get integer value
    def __GetIntegerValue(self, sHardwareName):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Call the raw function
        return self.__GetIntegerValueRaw(int(pHardware["location"]))

    # Get integer value raw
    def __GetIntegerValueRaw(self, nAddress):
        # Make sure the address is within range
        if (nAddress < self.__nMemoryLower) or (nAddress >= self.__nMemoryUpper):
            print "Offset out of range"
            return

        # Extract the return the value
        sWord = self.__sState[((nAddress - self.__nMemoryLower) * 4):((nAddress - self.__nMemoryLower + 1) * 4)]
        return int(sWord, 0x10)

    # Get analog value
    def __GetAnalogValue(self, sHardwareName):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calculate the absolute address of the target word
        nAbsoluteWordOffset = self.__DetermineHardwareOffset(pHardware) +  int(pHardware["location"])
        
        # Extract the return the value
        sWord = self.__sState[((nAbsoluteWordOffset - self.__nMemoryLower) * 4):((nAbsoluteWordOffset - self.__nMemoryLower + 1) * 4)]
        return int(sWord, 0x10)

    # Get thermocontroller values
    def __GetHeaterOn(self, sReactor, sHeater):
        # Read the stop bit
        nWordOffset, nBitOffset = self.__LoopUpHeaterStop(sReactor, sHeater)
        return (self.__GetBinaryValueRaw(nWordOffset, nBitOffset) == False)
    def __GetThermocontrollerSetValue(self, sHardwareName):
        # Look up the temperature set offset and return the value
        nOffset = self.__LookUpThermocontrollerSetOffset(sHardwareName)
        sWord = self.__sState[((nOffset - self.__nMemoryLower) * 4):((nOffset - self.__nMemoryLower + 1) * 4)]
        return int(sWord, 0x10)
    def __GetThermocontrollerActualValue(self, sHardwareName):
        # Look up the temperature actual offset and return the value
        nOffset = self.__LookUpThermocontrollerActualOffset(sHardwareName)
        sWord = self.__sState[((nOffset - self.__nMemoryLower) * 4):((nOffset - self.__nMemoryLower + 1) * 4)]
        return int(sWord, 0x10)

    # Get vacuum
    def __GetVacuum(self):
        nVacuumPLC = float(self.__GetAnalogValue("VacuumPressure"))
        return ((nVacuumPLC * self.__nVacuumGaugeSlope) + self.__nVacuumGaugeIntercept)

    # Get pressure regulator values
    def __GetPressureRegulatorSetPressure(self, nPressureRegulator):
        nPressurePLC = float(self.__GetAnalogValue("PressureRegulator" + str(nPressureRegulator) + "_SetPressure"))
        return ((nPressurePLC - self.__nPressureRegulatorSetIntercept) / self.__nPressureRegulatorSetSlope)
    def __GetPressureRegulatorActualPressure(self, nPressureRegulator):
        nPressurePLC = float(self.__GetAnalogValue("PressureRegulator" + str(nPressureRegulator) + "_ActualPressure"))
        return ((nPressurePLC * self.__nPressureRegulatorActualSlope) + self.__nPressureRegulatorActualIntercept)

    # Get reagent robot positions
    def __GetReagentReactorSetX(self):
        return self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__nReagentXAxis * 4))
    def __GetReagentReactorSetZ(self):
        return self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__nReagentZAxis * 4))
    def __GetReagentReactorActualX(self):
        return self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentXAxis * 4))
    def __GetReagentReactorActualZ(self):
        return self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentZAxis * 4))

    # Get reactor robot positions
    def __GetReactorRobotSetPosition(self, nReactor):
        return self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__LookUpReactorAxis(nReactor) * 4))
    def __GetReactorRobotActualPosition(self, nReactor):
        return self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__LookUpReactorAxis(nReactor) * 4))

    # Get the robot status
    def __GetRobotStatus(self, nAxis):
        return self.__GetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4))

    ### Support functions ###
        
    # Look up the reactor axis
    def __LookUpReactorAxis(self, nReactor):
        if (nReactor == 1):
            return self.__nReactor1Axis
        elif (nReactor == 2):
            return self.__nReactor2Axis
        elif (nReactor == 3):
            return self.__nReactor3Axis
        else:
            raise Exception("Invalid reactor")

    # Look up the reactor cassette X offset
    def __LookUpReactorCassetteXOffset(self, nReactor):
        if (nReactor == 1):
            return self.__nReactor1CassetteXOffset
        elif (nReactor == 2):
            return self.__nReactor2CassetteXOffset
        elif (nReactor == 3):
            return self.__nReactor3CassetteXOffset
        else:
            raise Exception("Invalid reactor")

    # Look up the reactor cassette Z offset
    def __LookUpReactorCassetteZOffset(self, nReactor):
        if (nReactor == 1):
            return self.__nReactor1CassetteZOffset
        elif (nReactor == 2):
            return self.__nReactor2CassetteZOffset
        elif (nReactor == 3):
            return self.__nReactor3CassetteZOffset
        else:
            raise Exception("Invalid reactor")

    # Calculates the memory range used by the PLC modules
    def __CalculateMemoryRange(self):
        # Create array of minimum and maximum memory offsets for each module
        pAddressArray = []

        # Digital out
        pAddressArray += [self.__nDigitalOutOffset]
        pAddressArray += [self.__nDigitalOutOffset + DIGITALOUT_SIZE]

        # Digital in
        pAddressArray += [self.__nDigitalInOffset]
        pAddressArray += [self.__nDigitalInOffset + DIGITALIN_SIZE]

        # Analog out
        nHardwareOffset = self.__CalculateHardwareOffset(self.__nAnalogOutUnit);
        pAddressArray += [nHardwareOffset]
        pAddressArray += [nHardwareOffset + ANALOGOUT_SIZE]

        # Analog in
        nHardwareOffset = self.__CalculateHardwareOffset(self.__nAnalogInUnit);
        pAddressArray += [nHardwareOffset]
        pAddressArray += [nHardwareOffset + ANALOGIN_SIZE]

        # Thermocontroller 1
        nHardwareOffset = self.__CalculateHardwareOffset(self.__nThermocontroller1Unit);
        pAddressArray += [nHardwareOffset]
        pAddressArray += [nHardwareOffset + THERMOCONTROLLER_SIZE]

        # Thermocontroller 2
        nHardwareOffset = self.__CalculateHardwareOffset(self.__nThermocontroller2Unit);
        pAddressArray += [nHardwareOffset]
        pAddressArray += [nHardwareOffset + THERMOCONTROLLER_SIZE]

        # Thermocontroller 3
        nHardwareOffset = self.__CalculateHardwareOffset(self.__nThermocontroller3Unit);
        pAddressArray += [nHardwareOffset]
        pAddressArray += [nHardwareOffset + THERMOCONTROLLER_SIZE]

        # RoboNet
        pAddressArray += [ROBONET_MIN]
        pAddressArray += [ROBONET_MAX]
        
        # Format and return the minimum and maximum values
        return min(pAddressArray), max(pAddressArray)

    # Look up hardware name details
    def __LookUpHardwareName(self, sHardwareName):
        try:
            # Extract the hardware descriptor string
            pHardwareNameComponents = sHardwareName.split("_")
            if len(pHardwareNameComponents) == 1:
                sHardwareDescriptor = str(self.__pHardwareMap[pHardwareNameComponents[0]])
            elif len(pHardwareNameComponents) == 2:
                sHardwareDescriptor = str(self.__pHardwareMap[pHardwareNameComponents[0]][pHardwareNameComponents[1]])
            elif len(pHardwareNameComponents) == 3:
                sHardwareDescriptor = str(self.__pHardwareMap[pHardwareNameComponents[0]][pHardwareNameComponents[1]][pHardwareNameComponents[2]])
            else:
                raise Exception("Too many components")

            # Convert the descriptor string to a dictionary object
            pDescriptorComponents = sHardwareDescriptor.split(".")
            if len(pDescriptorComponents) < 3:
                raise Exception("Invalid hardware entry")
            sType = str(pDescriptorComponents[0])
            pHardware = {"name":sHardwareName,
                "type":sType}
            if (sType == "binary") or (sType == "analog"):
                pHardware["access"] = str(pDescriptorComponents[1])
                pHardware["location"] = str(pDescriptorComponents[2])
            elif sType == "thermocontroller":
                pHardware["thermocontroller"] = str(pDescriptorComponents[1])
                pHardware["loop"] = str(pDescriptorComponents[2])
            else:
                raise Exception("Unknown hardware type")
            return pHardware
        except Exception as ex:
            # Raise an appropriate error
            raise Exception("Failed to look up hardware name: " + str(sHardwareName) + " (" + str(ex) + ")")

    # Look up robot position
    def __LookUpRobotPosition(self, sPositionName):
        try:
            # Extract the robot position descriptor string
            pPositionNameComponents = sPositionName.split("_")
            if len(pPositionNameComponents) == 1:
                sPositionDescriptor = str(self.__pRobotPositions[pPositionNameComponents[0]])
            elif len(pPositionNameComponents) == 2:
                sPositionDescriptor = str(self.__pRobotPositions[pPositionNameComponents[0]][pPositionNameComponents[1]])
            else:
                raise Exception("Too many components")

            # Convert the descriptor string to a dictionary object
            pDescriptorComponents = sPositionDescriptor.split("_")
            if len(pDescriptorComponents) == 1:
                return {"name":sPositionName,
                    "z":str(pDescriptorComponents[0])}
            elif len(pDescriptorComponents) == 2:
                return {"name":sPositionName,
                    "x":str(pDescriptorComponents[0]),
                    "z":str(pDescriptorComponents[1])}
            else:
                raise Exception()
        except Exception as ex:
            # Raise an appropriate error
            raise Exception("Failed to look up robot position: " + str(sPositionName) + " (" + str(ex) + ")")

    # Calculates the hardware offset from the module unit number
    def __CalculateHardwareOffset(self, nModuleUnit):
        return (2000 + (10 * nModuleUnit))

    # Determines the hardware module offset
    def __DetermineHardwareOffset(self, pHardware):
        nOffset = 0
        if pHardware["type"] == "binary":
            if pHardware["access"] == "in":
                nOffset = self.__nDigitalInOffset
            elif pHardware["access"] == "out":
                nOffset = self.__nDigitalOutOffset
        elif pHardware["type"] == "analog":
            if pHardware["access"] == "in":
                nOffset = self.__CalculateHardwareOffset(self.__nAnalogInUnit)
            elif pHardware["access"] == "out":
                nOffset = self.__CalculateHardwareOffset(self.__nAnalogOutUnit)
        elif pHardware["type"] == "thermocontroller":
            if pHardware["thermocontroller"] == "1":
                nOffset = self.__CalculateHardwareOffset(self.__nThermocontroller1Unit)
            elif pHardware["thermocontroller"] == "2":
                nOffset = self.__CalculateHardwareOffset(self.__nThermocontroller2Unit)
            elif pHardware["thermocontroller"] == "3":
                nOffset = self.__CalculateHardwareOffset(self.__nThermocontroller3Unit)
        return nOffset
        
    # Look up the heater stop bit
    def __LoopUpHeaterStop(self, nReactor, nHeater):
        # Look up the hardware by name
        pHardware = self.__LookUpHardwareName("Reactor" + str(nReactor) + "_TemperatureController" + str(nHeater))

        # Calculate the absolute address of the target word
        nWordOffset = self.__DetermineHardwareOffset(pHardware)
        if pHardware["loop"] == "1":
            return (nWordOffset + 0x2), 0x6
        elif pHardware["loop"] == "2":
            return (nWordOffset + 0x2), 0x4
        elif pHardware["loop"] == "3":
            return (nWordOffset + 0xc), 0x6
        elif pHardware["loop"] == "4":
            return (nWordOffset + 0xc), 0x4
        else:
            raise Exception("Invalid thermocontroller loop")

    # Look up the temperature set offset
    def __LookUpThermocontrollerSetOffset(self, sHardwareName):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calculate the absolute address of the target word
        nOffset = self.__DetermineHardwareOffset(pHardware)
        if pHardware["loop"] == "1":
            return nOffset
        elif pHardware["loop"] == "2":
            return (nOffset + 0x1)
        elif pHardware["loop"] == "3":
            return (nOffset + 0xa)
        elif pHardware["loop"] == "4":
            return (nOffset + 0xb)
        else:
            raise Exception("Invalid thermocontroller loop")

    # Look up the temperature actual offset
    def __LookUpThermocontrollerActualOffset(self, sHardwareName):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calculate the absolute address of the target word
        nOffset = self.__DetermineHardwareOffset(pHardware)
        if pHardware["loop"] == "1":
            return (nOffset + 0x3)
        elif pHardware["loop"] == "2":
            return (nOffset + 0x4)
        elif pHardware["loop"] == "3":
            return (nOffset + 0xd)
        elif pHardware["loop"] == "4":
           return (nOffset + 0xe)
        else:
            raise Exception("Invalid thermocontroller loop")
