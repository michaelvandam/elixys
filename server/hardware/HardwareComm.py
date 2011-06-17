""" ElixysHardwareComm.py

Implements the HardwareComm interface for the Elixys hardware """

### Imports
from configobj import ConfigObj
from SocketThread import SocketThread
import threading

### Constants

# Port we listen for the PLC on
PLC_IP = "192.168.250.1" # "127.0.0.1"
PLC_PORT = 9600
SERVER_PORT = 9600

# Constants for PLC command formatting
ICF = "80"    #Info Ctrl Field - Binary 80 or 81 [1][0 =Cmd 1=Resp][00000][0 or 1=Resp Req]                      
RSV = "00"    #Reserved - Always Zero
GCT = "02"    #Gateway Count - Set to 02 (or do not set?!)
DNET = "00"   #Dest. Network - 00 (Local Network)
DNODE = "01"  #Dest. Node - Ethernet IP?
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
        self.__pHardwareMap = ConfigObj("HardwareMap.ini")
        self.__pRobotPositions = ConfigObj("RobotPositions.ini")

        # Extract the module offsets
        self.__nDigitalOutOffset = int(self.__pHardwareMap["DigitalOutOffset"], 16)
        self.__nDigitalInOffset = int(self.__pHardwareMap["DigitalInOffset"], 16)
        self.__nAnalogOutOffset = int(self.__pHardwareMap["AnalogOutOffset"], 16)
        self.__nAnalogInOffset = int(self.__pHardwareMap["AnalogInOffset"], 16)
        self.__nThermocontroller1Offset = int(self.__pHardwareMap["Thermocontroller1Offset"], 16)
        self.__nThermocontroller2Offset = int(self.__pHardwareMap["Thermocontroller2Offset"], 16)
        self.__nThermocontroller3Offset = int(self.__pHardwareMap["Thermocontroller3Offset"], 16)
        self.__nRobotNetOffset = int(self.__pHardwareMap["RobotNetOffset"], 16)

        # Calculate the memory address range
        pMemoryRangeComponents = self.__CalculateMemoryRange().split(",")
        self.__nMemoryLower = int(pMemoryRangeComponents[0])
        self.__nMemoryUpper = int(pMemoryRangeComponents[1])

    ### Public functions ###

    # Startup/shutdown
    def StartUp(self, bResetSystem = True):
        # Spawn the socket thread
        self.__pSocketThread = SocketThread()
        self.__pSocketThreadTerminateEvent = threading.Event()
        self.__pSocketThread.SetParameters(PLC_IP, PLC_PORT, SERVER_PORT, self, self.__pSocketThreadTerminateEvent)
        self.__pSocketThread.start()
    def ShutDown(self):
        # Stop the socket thread
        self.__pSocketThreadTerminateEvent.set()
        self.__pSocketThread.join()

    # Update state
    def UpdateState(self):
        # Format and send the raw command to read the PLC memory
        sCommand = "0101B0"
        sCommand = sCommand + ("%0.4X" % self.__nMemoryLower)
        sCommand = sCommand + "00"
        sCommand = sCommand + ("%0.4X" % (self.__nMemoryUpper - self.__nMemoryLower))
        self.__SendRawCommand(sCommand)

    # Valves
    def OpenValve(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName, True)
    def CloseValve(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName, False)

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
    def PressureRegulatorOn(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_On", True)
    def PressureRegulatorOff(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_On", False)
    def SetPressureRegulatorPressure(self, sHardwareName, fPressure):
        pass

    # Reagent robot motion
    def MoveReagentRobotToPosition(self, sPositionName):
        pPosition = self.__LookUpRobotPosition(sPositionName)
        self.__MoveToAbsolutePosition("ReagentRobot_SetX", pPosition["x"])
        self.__MoveToAbsolutePosition("ReagentRobot_SetZ", pPosition["z"])
    def GripperUp(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", True)
    def GripperDown(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", False)
    def GripperOpen(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", True)
    def GripperClose(self):
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", False)

    # Reactor motion
    def MoveReactorToPosition(self, sPositionName):
        pPosition = self.__LookUpRobotPosition(sPositionName)
        sReactor = sPositionName.split("_")[0]
        self.__MoveToAbsolutePosition(sReactor + "_SetZ", pPosition["z"])
    def ReactorUp(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetReactorUp", True)
    def ReactorDown(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetReactorUp", False)

    # Temperature controllers
    def HeaterOn(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetHeaterOn", True)
    def HeaterOff(self, sHardwareName):
        self.__SetBinaryValue(sHardwareName + "_SetHeaterOn", False)
    def SetHeaterSetPoint(self, sHardwareName, fSetPoint):
        pass

    # Stir motor
    def SetMotorSpeed(self, sHardwareName, nMotorSpeed):
        pass

    # Radiation detector
    def UpdateRadiationDetector(self, sHardwareName):
        pass

    ### Private functions ###

    # Calculates the memory range used by the PLC modules
    def __CalculateMemoryRange(self):
        pAddressArray = [self.__nDigitalOutOffset,
            self.__nDigitalOutOffset + 0x8,
            self.__nDigitalInOffset,
            self.__nDigitalInOffset + 0x8,
            self.__nAnalogOutOffset,
            self.__nAnalogOutOffset + 0x8,
            self.__nAnalogInOffset,
            self.__nAnalogInOffset + 0x8,
            self.__nThermocontroller1Offset,
            self.__nThermocontroller1Offset + 0x8,
            self.__nThermocontroller2Offset,
            self.__nThermocontroller2Offset + 0x8,
            self.__nThermocontroller3Offset,
            self.__nThermocontroller3Offset + 0x8,
            self.__nRobotNetOffset,
            self.__nRobotNetOffset+ 0x8]
        return str(min(pAddressArray)) + "," + str(max(pAddressArray))

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
                raise Exception()

            # Convert the descriptor string to a dictionary object
            pDescriptorComponents = sHardwareDescriptor.split(".")
            if len(pDescriptorComponents) != 3:
                raise Exception()
            return {"name":sHardwareName,
                "type":str(pDescriptorComponents[0]),
                "access":str(pDescriptorComponents[1]),
                "location":str(pDescriptorComponents[2])}
        except Exception as ex:
            # Raise an appropriate error
            raise Exception("Failed to look up hardware name: " + str(sHardwareName))

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
                raise Exception()

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
            raise Exception("Failed to look up robot position: " + str(sPositionName))

    # Determines the hardware module offset
    def __DetermineHardwareModuleOffset(self, pHardware):
        nModuleOffset = 0
        if pHardware["type"] == "binary":
            if pHardware["access"] == "in":
                nModuleOffset = self.__nDigitalInOffset
            elif pHardware["access"] == "out":
                nModuleOffset = self.__nDigitalOutOffset
        elif pHardware["type"] == "integer":
            # Thermocontrollers?  RobotNet?
            #self.__nThermocontroller1Offset
            #self.__nThermocontroller2Offset
            #self.__nThermocontroller3Offset
            #self.__nRobotNetOffset
            pass
        elif pHardware["type"] == "analog":
            if pHardware["access"] == "in":
                nModuleOffset = self.__nAnalogInOffset
            elif pHardware["access"] == "out":
                nModuleOffset = self.__nAnalogOutOffset
        return nModuleOffset

    # Set binary value
    def __SetBinaryValue(self, sHardwareName, bValue):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calcuate the absolute address of the target bit
        nRelativeBitOffset = int(pHardware["location"])
        nAbsoluteBitOffset = nRelativeBitOffset % 0x10
        nAbsoluteByteOffset = self.__DetermineHardwareModuleOffset(pHardware) + ((nRelativeBitOffset - nAbsoluteBitOffset) / 0x10)

        # Format and send the raw command
        sCommand = "010230"
        sCommand = sCommand + ("%0.4X" % nAbsoluteByteOffset)
        sCommand = sCommand + ("%0.2X" % nAbsoluteBitOffset)
        sCommand = sCommand + "0001"
        if bValue:
            sCommand = sCommand + "01" 
        else:
            sCommand = sCommand + "00"
        self.__SendRawCommand(sCommand)

    # Set integer value
    def __SetIntegerValue(self, sHardwareName, nValue):
        print "Implement SetIntegerValue (" + sHardwareName + ")"

    # Set analog value
    def __SetAnalogValue(self, sHardwareName, fValue):
        print "Implement SetAnalogValue (" + sHardwareName + ")"

    # Get binary value
    def __GetBinaryValue(self, sHardwareName, sState):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calcuate the absolute address of the target bit
        nRelativeBitOffset = int(pHardware["location"])
        nAbsoluteBitOffset = nRelativeBitOffset % 0x10
        nAbsoluteByteOffset = self.__DetermineHardwareModuleOffset(pHardware) + ((nRelativeBitOffset - nAbsoluteBitOffset) / 0x10)

        # Make sure the address is within range
        if (nAbsoluteByteOffset < self.__nMemoryLower) or (nAbsoluteByteOffset >= self.__nMemoryUpper):
            print "Offset out of range"
            return

        # Extract the return the value
        sByte = sState[(nAbsoluteByteOffset - self.__nMemoryLower):(nAbsoluteByteOffset - self.__nMemoryLower + 4)]
        nByte = int(sByte, 0x10)
        nBit = (nByte >> nAbsoluteBitOffset) & 1
        return nBit != 0

    # Get integer value
    def __GetIntegerValue(self, sHardwareName, sState):
        print "Implement SetIntegerValue (" + sHardwareName + ")"

    # Get analog value
    def __GetAnalogValue(self, sHardwareName, sState):
        print "Implement SetAnalogValue (" + sHardwareName + ")"

    # Move robot to absolute position
    def __MoveToAbsolutePosition(self, sHardwareName, nAbsolutePosition):
        print "Implement MoveToAbsolutePosition (" + sHardwareName + " = " + str(nAbsolutePosition) + ")"

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
            print "Sending packet",
            if sPacket[20:24] in PLCCOMMANDS:
                print ("(%s)" % PLCCOMMANDS[sPacket[20:24]])
            else:
                print ("(unknown command %s)" % sPacket[20:24])
            self.__pSocketThread.SendPacket(sBinaryPacket)
        except Exception as ex:
            # Display the error
            print "Failed to send packet to PLC (" + str(ex) + ")"

    # Processes a raw response from the PLC
    def __ProcessRawResponse(self, sResponse):
        # Strip the header info off the response and check for errors
        sResponse = sResponse[20:]
        sError = sResponse[4:8]
        if sError == "0000":
            # Operation successful
            print "Successful response received"
        else:
            # Error encountered
            if sError in PLCERRORS:
                raise Exception("PLC error: " + PLC_ERRORS(sError))
            else:
                raise Exception("PLC error: " + sError)

        # Discard responses that are too short
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

    def __ProcessRawState(self, sState):
        # Format the state into a string for the moment
        self.sState = "\nCurrent state:\n"
        self.sState += "  Door1Open: " + str(self.__GetBinaryValue("Door1Open", sState)) + "\n"
        self.sState += "  Door2Open: " + str(self.__GetBinaryValue("Door2Open", sState)) + "\n"
        self.sState += "  PressureRegulator1:\n"
        self.sState += "    ActualPressure: TBD\n" #PressureRegulator1_ActualPressure = analog.in.0
        self.sState += "  PressureRegulator2:\n"
        self.sState += "    ActualPressure: TBD\n" #PressureRegulator2_ActualPressure = analog.in.1
        self.sState += "  ReagentRobot:\n"
        self.sState += "    ActualX: TBD\n" #ReagentRobot_ActualX = integer.in.0
        self.sState += "    ActualZ: TBD\n" #ReagentRobot_ActualZ = integer.in.1
        self.sState += "    GripperUp: " + str(self.__GetBinaryValue("ReagentRobot_GripperUp", sState)) + "\n"
        self.sState += "    GripperDown: " + str(self.__GetBinaryValue("ReagentRobot_GripperDown", sState)) + "\n"
        self.sState += "    GripperOpen: " + str(self.__GetBinaryValue("ReagentRobot_GripperOpen", sState)) + "\n"
        self.sState += "    GripperClose: " + str(self.__GetBinaryValue("ReagentRobot_GripperClose", sState)) + "\n"
        self.sState += "  Reactor1:\n"
        self.sState += "    ReactorUp: " + str(self.__GetBinaryValue("Reactor1_ReactorUp", sState)) + "\n"
        self.sState += "    ReactorDown: " + str(self.__GetBinaryValue("Reactor1_ReactorDown", sState)) + "\n"
        self.sState += "    RadiationDetector: TBD\n" #Reactor1_RadiationDetector = analog.in.2
        self.sState += "    TemperatureController1:\n"
        self.sState += "      ActualTemperature: TBD\n" #Reactor1_TemperatureController1.ActualTemperature = integer.in.3
        self.sState += "    TemperatureController2:\n"
        self.sState += "      ActualTemperature: TBD\n" #Reactor1_TemperatureController2.ActualTemperature = integer.in.4
        self.sState += "    TemperatureController3:\n"
        self.sState += "      ActualTemperature: TBD\n" #Reactor1_TemperatureController3.ActualTemperature = integer.in.5

        self.sState += "\nSet values:\n"
        self.sState += "  VacuumSystemOn: " + str(self.__GetBinaryValue("VacuumSystemOn", sState)) + "\n"
        self.sState += "  CoolingSystemOn: " + str(self.__GetBinaryValue("CoolingSystemOn", sState)) + "\n"
        self.sState += "  PressureRegulator1:\n"
        self.sState += "    On: " + str(self.__GetBinaryValue("PressureRegulator1_On", sState)) + "\n"
        self.sState += "    SetPressure: TBD\n" #PressureRegulator1_SetPressure = analog.in.0
        self.sState += "  PressureRegulator2:\n"
        self.sState += "    On: " + str(self.__GetBinaryValue("PressureRegulator2_On", sState)) + "\n"
        self.sState += "    SetPressure: TBD:\n" #PressureRegulator2_SetPressure = analog.out.1
        self.sState += "  ReagentRobot:\n"
        self.sState += "    SetX: TBD\n" #ReagentRobot_SetX = integer.out.0
        self.sState += "    SetZ: TBD\n" #ReagentRobot_SetZ = integer.out.1
        self.sState += "    SetGripperUp: " + str(self.__GetBinaryValue("ReagentRobot_SetGripperUp", sState)) + "\n"
        self.sState += "    SetGripperOpen: " + str(self.__GetBinaryValue("ReagentRobot_SetGripperOpen", sState)) + "\n"
        self.sState += "  Reactor1:\n"
        self.sState += "    SetZ: TBD\n" #Reactor1_SetZ = integer.out.2
        self.sState += "    SetReactorUp: " + str(self.__GetBinaryValue("Reactor1_SetReactorUp", sState)) + "\n"
        self.sState += "    EvaporationValve: " + str(self.__GetBinaryValue("Reactor1_EvaporationValve", sState)) + "\n"
        self.sState += "    VacuumValve: " + str(self.__GetBinaryValue("Reactor1_VacuumValve", sState)) + "\n"
        self.sState += "    TransferValve: " + str(self.__GetBinaryValue("Reactor1_TransferValve", sState)) + "\n"
        self.sState += "    Reagent1TransferValve: " + str(self.__GetBinaryValue("Reactor1_Reagent1TransferValve", sState)) + "\n"
        self.sState += "    Reagent2TransferValve: " + str(self.__GetBinaryValue("Reactor1_Reagent2TransferValve", sState)) + "\n"
        self.sState += "    Stopcock1Valve: " + str(self.__GetBinaryValue("Reactor1_Stopcock1Valve", sState)) + "\n"
        self.sState += "    Stopcock2Valve: " + str(self.__GetBinaryValue("Reactor1_Stopcock2Valve", sState)) + "\n"
        self.sState += "    Stopcock3Valve: " + str(self.__GetBinaryValue("Reactor1_Stopcock3Valve", sState)) + "\n"
        self.sState += "    StirMotor: TBD\n" #Reactor1_StirMotor = integer.out.3
        self.sState += "    RadiationDetector: TBD\n" #Reactor1_RadiationDetector = analog.in.2
        self.sState += "    TemperatureController1:\n"
        self.sState += "      SetHeaterOn: " + str(self.__GetBinaryValue("Reactor1_TemperatureController1_SetHeaterOn", sState)) + "\n"
        self.sState += "      SetTemperature: TBD\n" #Reactor1_TemperatureController1.SetTemperature = integer.out.4
        self.sState += "    TemperatureController2:\n"
        self.sState += "      SetHeaterOn: " + str(self.__GetBinaryValue("Reactor1_TemperatureController2_SetHeaterOn", sState)) + "\n"
        self.sState += "      SetTemperature: TBD\n" #Reactor1_TemperatureController2.SetTemperature = integer.out.5
        self.sState += "    TemperatureController3:\n"
        self.sState += "      SetHeaterOn: " + str(self.__GetBinaryValue("Reactor1_TemperatureController3_SetHeaterOn", sState)) + "\n"
        self.sState += "      SetTemperature: TBD\b" #Reactor1_TemperatureController3.SetTemperature = integer.out.6
		
        print self.sState
        print "\nRaw state:\n" + sState
