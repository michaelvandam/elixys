""" ElixysHardwareComm.py

Implements the HardwareComm interface for the Elixys hardware """

### Imports ###
from configobj import ConfigObj
from SocketThread import SocketThread
import threading
import time
import os.path
import sys

### Constants ###

# IP and port of the PLC.  Make sure only one PLC IP is defined
PLC_IP = "192.168.1.200"    # Real PLC
#PLC_IP = "127.0.0.1"        # Fake PLC for testing and demo
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
ROBONET_MAX = 3312 + (5 * 4)
ROBONET_ENABLE = 3201
ROBONET_CONTROL = 3212
ROBONET_AXISPOSSET = 3209
ROBONET_AXISPOSREAD = 3309
ROBONET_CHECK = 3312
ROBONET_INIT = 0x4000
ROBONET_ERROR1 = 0x400A
ROBONET_SERVOON = 0x4011
ROBONET_ERROR2 = 0x4013
ROBONET_HOMING = 0x4014
ROBONET_DISABLED = 0x7002
ROBONET_ENABLED1 = 0x7012
ROBONET_ENABLED2 = 0x7013
ROBONET_MOVING = 0x7016
ROBONET_ERROR3 = 0x700A

# Robot position hit test limit
ROBOT_POSITION_LIMIT = 20

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

    ### Construction/Destruction ###

    def __init__(self, sHardwareDirectory):
        # Load the hardware map and robot positions
        sHardwareMap = sHardwareDirectory + "HardwareMap.ini"
        sRobotPositions = sHardwareDirectory + "RobotPositions.ini"
        if not os.path.exists(sHardwareMap) or not os.path.exists(sRobotPositions):
            print "Invalid path to INI files"
            return
        self.__pHardwareMap = ConfigObj(sHardwareMap)
        self.__pRobotPositions = ConfigObj(sRobotPositions)

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
        self.__nRadiationDetectorSlope = float(self.__pHardwareMap["RadiationDetectorSlope"])
        self.__nRadiationDetectorIntercept = float(self.__pHardwareMap["RadiationDetectorIntercept"])

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
        self.__nMemoryLower, self.__nMemoryUpper = self.CalculateMemoryRange()

        # Initialize our variables
        self.__pSystemModel = None
        self.__nStateOffset = 0
        self.__sState = ""
        self.__FakePLC_pMemory = None
        self.__FakePLC_nMemoryLower = 0
        self.__FakePLC_nMemoryUpper = 0
        
    ### Public functions ###

    def StartUp(self):
        # Spawn the socket thread
        self.__pSocketThread = SocketThread()
        self.__pSocketThreadTerminateEvent = threading.Event()
        self.__pSocketThread.SetParameters(PLC_IP, PLC_PORT, self, self.__pSocketThreadTerminateEvent)
        self.__pSocketThread.setDaemon(True)
        self.__pSocketThread.start()
        
        # Enable analog out
        self.__SetIntegerValueRaw(2000, 255);
        
        # Enable RoboNet control for all axes
        self.__SetIntegerValueRaw(ROBONET_ENABLE, 0x8000)

    def ShutDown(self):
        # Stop the socket thread
        self.__pSocketThreadTerminateEvent.set()
        self.__pSocketThread.join()
        
    # Set the system model
    def SetSystemModel(self, pSystemModel):
        self.__pSystemModel = pSystemModel

    # Calculates the memory range used by the PLC modules
    def CalculateMemoryRange(self):
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
        
        # Return the minimum and maximum values
        return min(pAddressArray), max(pAddressArray)
        
    # Update state
    def UpdateState(self):
        # What mode are we in?
        if (self.__FakePLC_pMemory == None):
            # We are in normal mode.  Make sure we're not already in the process of updating the state
            if self.__sState != "":
                return

            # We're limited in the maximum amount of data we can read in a single request.  Start by requesting the
            # first chunk of the state
            self.__nStateOffset = self.__nMemoryLower
            self.__sState = ""
            self.__RequestNextStateChunk()
        else:
            # We are in fake PLC mode.  Format our fake memory into a string
            sMemory = ""
            for nOffset in range(self.__FakePLC_nMemoryLower, self.__FakePLC_nMemoryUpper + 1):
                sMemory += ("%0.4X" % self.__FakePLC_pMemory[nOffset - self.__nMemoryLower])
            
            # Pass the fake memory to the state processing function
            self.__nStateOffset = self.__nMemoryLower
            self.__sState = ""
            self.__ProcessRawState(sMemory)

    ### Hardware control functions ###
    
    # Vacuum system (currently not implemented in the hardware)
    def VacuumSystemOn(self):
        pass
        #self.__SetBinaryValue("VacuumSystemOn", True)
    def VacuumSystemOff(self):
        pass
        #self.__SetBinaryValue("VacuumSystemOn", False)

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
        if nPressurePLC > 4200:
            nPressurePLC = 4200
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
    def MoveRobotToHome(self):
        self.__SetRobotPosition(self.__nReagentXAxis, 0)
        self.__SetRobotPosition(self.__nReagentZAxis, 0)
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
        nReactorOffset = self.__LookUpReactorOffset(nReactor)
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
    def ReactorStopcockPosition(self, nReactor, nStopcock, nPosition):
        if nPosition == 1:
            self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValvePosition2", False)
            time.sleep(0.1)
            self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValvePosition1", True)
        elif nPosition == 2:
            self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValvePosition1", False)
            time.sleep(0.1)
            self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValvePosition2", True)
        else:
            raise Exception("Invalid stopcock position")

    # Temperature controllers
    def HeaterOn(self, nReactor):
        # Clear the stop bit
        for nHeater in range(1, 4):
            nWordOffset, nBitOffset = self.__LoopUpHeaterStop(nReactor, nHeater)
            self.__SetBinaryValueRaw(nWordOffset, nBitOffset, 0)
    def HeaterOff(self, nReactor):
        # Set the stop bit
        for nHeater in range(1, 4):
            nWordOffset, nBitOffset = self.__LoopUpHeaterStop(nReactor, nHeater)
            self.__SetBinaryValueRaw(nWordOffset, nBitOffset, 1)
    def SetHeater(self, nReactor, nSetPoint):
        # Set the heater temperature
        for nHeater in range(1, 4):
            self.__SetThermocontrollerSetValue("Reactor" + str(nReactor) + "_TemperatureController" + str(nHeater), nSetPoint)

    # Stir motor
    def SetMotorSpeed(self, nReactor, nMotorSpeed):
        self.__SetAnalogValue("Reactor" + str(nReactor) + "_StirMotor", nMotorSpeed)

    # Home all robots
    def HomeRobots(self):
        print "Homing all axes"
        for nAxis in range(0, 5):
            # Turn on servo axis
            self.__SetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4), 0x10)
        time.sleep(0.1)
        for nAxis in range(0, 5):
            # Home axis
            self.__SetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4), 0x12)

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

    ### Fake PLC functions ###
    
    # Used by the fake PLC to set the PLC memory
    def FakePLC_SetMemory(self, pMemory, nMemoryLower, nMemoryUpper):
        print "Fake PLC set memory: " + str(nMemoryLower) + " - " + str(nMemoryUpper)
        # Make sure the memory ranges match up
        if (nMemoryLower != self.__nMemoryLower) or (nMemoryUpper != self.__nMemoryUpper):
            raise Exception("Memory range mismatch")

        # Remember the memory and range
        self.__FakePLC_pMemory = pMemory
        self.__FakePLC_nMemoryLower = nMemoryLower
        self.__FakePLC_nMemoryUpper = nMemoryUpper

    # Used by the fake PLC to read back a range of the fake memory
    def FakePLC_ReadMemory(self, nReadOffset, nReadLength):
        # Scan the memory range
        sMemory = ""
        for nOffset in range(self.__FakePLC_nMemoryLower, self.__FakePLC_nMemoryUpper + 1):
            if nOffset >= nReadOffset:
                # Stop when complete
                if nOffset > (nReadOffset + nReadLength):
                    break

                # Append the next word of data
                sMemory += ("%0.4X" % self.__FakePLC_pMemory[nOffset - self.__nMemoryLower])
        
        # Return the memory
        return sMemory
        
    # Used by the fake PLC to change the state of the system
    def FakePLC_SetVacuumPressure(self, nPressure):
        nPressurePLC = (nPressure - self.__nVacuumGaugeIntercept) / self.__nVacuumGaugeSlope
        self.__SetAnalogValue("VacuumPressure", nPressurePLC)
    def FakePLC_SetPressureRegulatorActualPressure(self, nPressureRegulator, nPressure):
        nPressurePLC = (nPressure - self.__nPressureRegulatorActualIntercept) / self.__nPressureRegulatorActualSlope
        self.__SetAnalogValue("PressureRegulator" + str(nPressureRegulator) + "_ActualPressure", nPressurePLC)
    def FakePLC_SetReagentRobotPosition(self, nPositionX, nPositionZ):
        print "Setting reagent robot position: " + str(nPositionX) + ", " + str(nPositionZ)
        self.__SetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentXAxis * 4), nPositionX)
        self.__SetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentZAxis * 4), nPositionZ)
    def FakePLC_EnableReactorRobot(self, nReactor):
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__LookUpReactorAxis(nReactor) * 4), ROBONET_ENABLED1)
    def FakePLC_DisableReactorRobot(self, nReactor):
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__LookUpReactorAxis(nReactor) * 4), ROBONET_DISABLED)
    def FakePLC_SetReactorLinearPosition(self, nReactor, nPositionZ):
        self.__SetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__LookUpReactorAxis(nReactor) * 4), nPositionZ)
    def FakePLC_SetReactorVerticalPosition(self, nReactor, bUpSensor, bDownSensor):
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_ReactorUp", bUpSensor)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_ReactorDown", bDownSensor)
    def FakePLC_SetReactorActualTemperature(self, nReactor, nTemperature):
        for nHeater in range(1, 4):
            nOffset = self.__LookUpThermocontrollerActualOffset("Reactor" + str(nReactor) + "_TemperatureController" + str(nHeater))
            self.__SetIntegerValueRaw(nOffset, nTemperature)
    def FakePLC_SetBinaryValue(self, nWordOffset, nBitOffset, bValue):
        self.__SetBinaryValueRaw(nWordOffset, nBitOffset, bValue)
    def FakePLC_SetWordValue(self, nWordOffset, nValue):
        self.__SetIntegerValueRaw(nWordOffset, nValue)

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
        # What mode are we in?
        if (self.__FakePLC_pMemory == None):
            # We are in normal mode.  Format and send the raw command to the PLC
            sCommand = "010230"					            # Write bit to CIO memory
            sCommand = sCommand + ("%0.4X" % nWordOffset)	# Memory offset (words)
            sCommand = sCommand + ("%0.2X" % nBitOffset)    # Memory offset (bits)
            sCommand = sCommand + "0001"				    # Number of bits to write
            if bValue:
                sCommand = sCommand + "01"				    # Set bit
            else:
                sCommand = sCommand + "00"				    # Clear bit
            self.__SendRawCommand(sCommand)
        else:
            # We are in fake PLC mode.  Validate the address
            if (nWordOffset < self.__FakePLC_nMemoryLower) or ((nWordOffset + self.__FakePLC_nMemoryLower) >= self.__FakePLC_nMemoryUpper):
                raise Exception("Invalid word offset")
            if nBitOffset > 15:
                raise Exception("Invalid bit offset")

            # Update the target bit in the fake memory
            if bValue:
                self.__FakePLC_pMemory[nWordOffset] = self.__FakePLC_pMemory[nWordOffset] | (bValue << nBitOffset)
            else:
                self.__FakePLC_pMemory[nWordOffset] = self.__FakePLC_pMemory[nWordOffset] & ~(1 << nBitOffset)

    # Set integer value by hardware name
    def __SetIntegerValue(self, sHardwareName, nValue):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Call the raw function
        self.__SetIntegerValueRaw(int(pHardware["location"]), nValue)

    # Set analog value
    def __SetAnalogValue(self, sHardwareName, nValue):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calculate the absolute address of the target word
        nAbsoluteWordOffset = self.__DetermineHardwareOffset(pHardware) + int(pHardware["location"])
        
        # Set the integer value
        self.__SetIntegerValueRaw(nAbsoluteWordOffset, int(nValue))
        
    # Set integer value raw
    def __SetIntegerValueRaw(self, nAddress, nValue):
        # What mode are we in?
        if (self.__FakePLC_pMemory == None):
            # We are in normal mode.  Format and send the raw command to the PLC
            sCommand = "0102B0"					                    # Write word to CIO memory
            sCommand = sCommand + ("%0.4X" % nAddress)              # Memory offset (words)
            sCommand = sCommand + "00"                              # Memory offset (bits)
            sCommand = sCommand + "0001"				            # Number of words to write
            sCommand = sCommand + ("%0.4X" % nValue)				# Set word
            self.__SendRawCommand(sCommand)
        else:
            # We are in fake PLC mode.  Validate the address
            if (nAddress < self.__FakePLC_nMemoryLower) or ((nAddress + self.__FakePLC_nMemoryLower) >= self.__FakePLC_nMemoryUpper):
                raise Exception("Invalid word offset")
            
            # Update the target word in the fake memory
            self.__FakePLC_pMemory[nAddress] = nValue

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

        # Make sure we have a system model
        if self.__pSystemModel == None:
            # No, so reset our state and return
            self.__nStateOffset = self.__nMemoryLower
            self.__sState = ""
            return
        
        # Acquire a lock on the system model
        pModel = self.__pSystemModel.LockSystemModel()

        # Perform the state update in a try/except/finally block to make sure we release our lock on the system model
        try:        
            # Look up our reagent robot positions
            nReagentRobotSetX = self.__GetReagentRobotSetX()
            nReagentRobotSetZ = self.__GetReagentRobotSetZ()
            nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery = \
                self.__LookUpReagentRobotPosition(nReagentRobotSetX, nReagentRobotSetZ)
            nReagentRobotActualX = self.__GetReagentRobotActualX()
            nReagentRobotActualZ = self.__GetReagentRobotActualZ()
            nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery = \
                self.__LookUpReagentRobotPosition(nReagentRobotActualX, nReagentRobotActualZ)

            # Look up our reactor robot positions
            nReactor1RobotSetPositionRaw = self.__GetReactorRobotSetPosition(1)
            nReactor1RobotActualPositionRaw = self.__GetReactorRobotActualPosition(1)
            nReactor1RobotSetPosition = self.__LookUpReactorRobotPosition(nReactor1RobotSetPositionRaw)
            nReactor1RobotActualPosition = self.__LookUpReactorRobotPosition(nReactor1RobotActualPositionRaw)
            nReactor2RobotSetPositionRaw = self.__GetReactorRobotSetPosition(2)
            nReactor2RobotActualPositionRaw = self.__GetReactorRobotActualPosition(2)
            nReactor2RobotSetPosition = self.__LookUpReactorRobotPosition(nReactor2RobotSetPositionRaw)
            nReactor2RobotActualPosition = self.__LookUpReactorRobotPosition(nReactor2RobotActualPositionRaw)
            nReactor3RobotSetPositionRaw = self.__GetReactorRobotSetPosition(3)
            nReactor3RobotActualPositionRaw = self.__GetReactorRobotActualPosition(3)
            nReactor3RobotSetPosition = self.__LookUpReactorRobotPosition(nReactor3RobotSetPositionRaw)
            nReactor3RobotActualPosition = self.__LookUpReactorRobotPosition(nReactor3RobotActualPositionRaw)

            # Update the system model
            pModel["CoolingSystem"].updateState(self.__GetBinaryValue("CoolingSystemOn"))
            pModel["VacuumSystem"].updateState(True, self.__GetVacuumPressure())
            pModel["ExternalSystems"].updateState(self.__GetBinaryValue("F18_Load"), self.__GetBinaryValue("F18_Elute"), self.__GetBinaryValue("HPLC_Load"))
            pModel["PressureRegulator1"].updateState(self.__GetPressureRegulatorSetPressure(1), self.__GetPressureRegulatorActualPressure(1))
            pModel["PressureRegulator2"].updateState(self.__GetPressureRegulatorSetPressure(2), self.__GetPressureRegulatorActualPressure(2))
            pModel["ReagentDelivery"].updateState(nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery,
                nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery, nReagentRobotSetX,
                nReagentRobotSetZ, nReagentRobotActualX, nReagentRobotActualZ, self.__GetBinaryValue("ReagentRobot_SetGripperUp"),
                self.__GetBinaryValue("ReagentRobot_SetGripperDown"), self.__GetBinaryValue("ReagentRobot_SetGripperOpen"),
                self.__GetBinaryValue("ReagentRobot_SetGripperClose"), self.__GetRobotStatus(self.__nReagentXAxis), self.__GetRobotStatus(self.__nReagentZAxis))
            pModel["Reactor1"]["Motion"].updateState(nReactor1RobotSetPosition, nReactor1RobotActualPosition, nReactor1RobotSetPositionRaw, nReactor1RobotActualPositionRaw,
                self.__GetBinaryValue("Reactor1_SetReactorUp"), self.__GetBinaryValue("Reactor1_SetReactorDown"), self.__GetBinaryValue("Reactor1_ReactorUp"),
                self.__GetBinaryValue("Reactor1_ReactorDown"), self.__GetRobotStatus(self.__LookUpReactorAxis(1)), self.__GetRobotControlWord(1), 
                self.__GetRobotCheckWord(1))
            pModel["Reactor1"]["Valves"].updateState(self.__GetBinaryValue("Reactor1_EvaporationNitrogenValve"), self.__GetBinaryValue("Reactor1_EvaporationVacuumValve"),
                self.__GetBinaryValue("Reactor1_TransferValve"), self.__GetBinaryValue("Reactor1_Reagent1TransferValve"), self.__GetBinaryValue("Reactor1_Reagent2TransferValve"))
            pModel["Reactor1"]["Stopcock1"].updateState(self.__GetBinaryValue("Reactor1_Stopcock1ValvePosition1"), self.__GetBinaryValue("Reactor1_Stopcock1ValvePosition2"))
            pModel["Reactor1"]["Stopcock2"].updateState(self.__GetBinaryValue("Reactor1_Stopcock2ValvePosition1"), self.__GetBinaryValue("Reactor1_Stopcock2ValvePosition2"))
            pModel["Reactor1"]["Stopcock3"].updateState(self.__GetBinaryValue("Reactor1_Stopcock3ValvePosition1"), self.__GetBinaryValue("Reactor1_Stopcock3ValvePosition2"))
            pModel["Reactor1"]["Stir"].updateState(self.__GetAnalogValue("Reactor1_StirMotor"))
            pModel["Reactor1"]["Thermocouple"].updateState(self.__GetHeaterOn(1, 1), self.__GetHeaterOn(1, 2), self.__GetHeaterOn(1, 3),
                self.__GetThermocontrollerSetValue("Reactor1_TemperatureController1"), self.__GetThermocontrollerSetValue("Reactor1_TemperatureController2"),
                self.__GetThermocontrollerSetValue("Reactor1_TemperatureController3"), self.__GetThermocontrollerActualValue("Reactor1_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor1_TemperatureController2"), self.__GetThermocontrollerActualValue("Reactor1_TemperatureController3"))
            pModel["Reactor1"]["Radiation"].updateState(self.__GetRadiation(1))
            pModel["Reactor2"]["Motion"].updateState(nReactor2RobotSetPosition, nReactor2RobotActualPosition, nReactor2RobotSetPositionRaw, nReactor2RobotActualPositionRaw,
                self.__GetBinaryValue("Reactor2_SetReactorUp"), self.__GetBinaryValue("Reactor2_SetReactorDown"), self.__GetBinaryValue("Reactor2_ReactorUp"),
                self.__GetBinaryValue("Reactor2_ReactorDown"), self.__GetRobotStatus(self.__LookUpReactorAxis(2)), self.__GetRobotControlWord(2), 
                self.__GetRobotCheckWord(2))
            pModel["Reactor2"]["Valves"].updateState(self.__GetBinaryValue("Reactor2_EvaporationNitrogenValve"), self.__GetBinaryValue("Reactor2_EvaporationVacuumValve"),
                self.__GetBinaryValue("Reactor2_TransferValve"), self.__GetBinaryValue("Reactor2_Reagent1TransferValve"), self.__GetBinaryValue("Reactor2_Reagent2TransferValve"))
            pModel["Reactor2"]["Stopcock1"].updateState(self.__GetBinaryValue("Reactor2_Stopcock1ValvePosition1"), self.__GetBinaryValue("Reactor2_Stopcock1ValvePosition2"))
            pModel["Reactor2"]["Stir"].updateState(self.__GetAnalogValue("Reactor2_StirMotor"))
            pModel["Reactor2"]["Thermocouple"].updateState(self.__GetHeaterOn(2, 1), self.__GetHeaterOn(2, 2), self.__GetHeaterOn(2, 3),
                self.__GetThermocontrollerSetValue("Reactor2_TemperatureController1"), self.__GetThermocontrollerSetValue("Reactor2_TemperatureController2"),
                self.__GetThermocontrollerSetValue("Reactor2_TemperatureController3"), self.__GetThermocontrollerActualValue("Reactor2_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor2_TemperatureController2"), self.__GetThermocontrollerActualValue("Reactor2_TemperatureController3"))
            pModel["Reactor2"]["Radiation"].updateState(self.__GetRadiation(2))
            pModel["Reactor3"]["Motion"].updateState(nReactor3RobotSetPosition, nReactor3RobotActualPosition, nReactor3RobotSetPositionRaw, nReactor3RobotActualPositionRaw,
                self.__GetBinaryValue("Reactor3_SetReactorUp"), self.__GetBinaryValue("Reactor3_SetReactorDown"), self.__GetBinaryValue("Reactor3_ReactorUp"),
                self.__GetBinaryValue("Reactor3_ReactorDown"), self.__GetRobotStatus(self.__LookUpReactorAxis(3)), self.__GetRobotControlWord(3), 
                self.__GetRobotCheckWord(3))
            pModel["Reactor3"]["Valves"].updateState(self.__GetBinaryValue("Reactor3_EvaporationNitrogenValve"), self.__GetBinaryValue("Reactor3_EvaporationVacuumValve"),
                self.__GetBinaryValue("Reactor3_TransferValve"), self.__GetBinaryValue("Reactor3_Reagent1TransferValve"), self.__GetBinaryValue("Reactor3_Reagent2TransferValve"))
            pModel["Reactor3"]["Stopcock1"].updateState(self.__GetBinaryValue("Reactor3_Stopcock1ValvePosition1"), self.__GetBinaryValue("Reactor3_Stopcock1ValvePosition2"))
            pModel["Reactor3"]["Stir"].updateState(self.__GetAnalogValue("Reactor3_StirMotor"))
            pModel["Reactor3"]["Thermocouple"].updateState(self.__GetHeaterOn(3, 1), self.__GetHeaterOn(3, 2), self.__GetHeaterOn(3, 3),
                self.__GetThermocontrollerSetValue("Reactor3_TemperatureController1"), self.__GetThermocontrollerSetValue("Reactor3_TemperatureController2"),
                self.__GetThermocontrollerSetValue("Reactor3_TemperatureController3"), self.__GetThermocontrollerActualValue("Reactor3_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor3_TemperatureController2"), self.__GetThermocontrollerActualValue("Reactor3_TemperatureController3"))
            pModel["Reactor3"]["Radiation"].updateState(self.__GetRadiation(3))

            # This chunk of code can be used to log the temperature of a specific thermocouple
            if True:
                if sys.platform == "win32":
                   sLogFile = "temp_profile.txt"
                else:
                   sLogFile = "/home/Elixys/Desktop/temp_profile.txt"
                nMeasureReactor = 2
                nLiquidReactor = 3
                nLiquidThermocouple = 1
                try:
                    self.__startTime
                except Exception, e:
                    self.__startTime = time.time()
                    f = open(sLogFile, "w")
                    f.write("Time,Heater1Set,Heater2Set,Heater3Set,Heater1Actual,Heater2Actual,Heater3Actual,Liquid\n")
                    f.flush()
                    f.close()
                currentTime = time.time()
                f = open(sLogFile, "a")
                f.write("%.1f"%(currentTime - self.__startTime) + "," + \
                    str(self.__GetThermocontrollerSetValue("Reactor" + str(nMeasureReactor) + "_TemperatureController1")) + "," + \
                    str(self.__GetThermocontrollerSetValue("Reactor" + str(nMeasureReactor) + "_TemperatureController2")) + "," + \
                    str(self.__GetThermocontrollerSetValue("Reactor" + str(nMeasureReactor) + "_TemperatureController3")) + "," + \
                    str(self.__GetThermocontrollerActualValue("Reactor" + str(nMeasureReactor) + "_TemperatureController1")) + "," + \
                    str(self.__GetThermocontrollerActualValue("Reactor" + str(nMeasureReactor) + "_TemperatureController2")) + "," + \
                    str(self.__GetThermocontrollerActualValue("Reactor" + str(nMeasureReactor) + "_TemperatureController3")) + "," + \
                    str(self.__GetThermocontrollerActualValue("Reactor" + str(nLiquidReactor) + "_TemperatureController" + str(nLiquidThermocouple))) + "," + "\n")
                f.flush()
                f.close()
            
        finally:
            # Release the system model lock
            self.__pSystemModel.UnlockSystemModel()
            self.__pSystemModel.ModelUpdated()
        
        # Reset our state
        self.__nStateOffset = self.__nMemoryLower
        self.__sState = ""

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
        if sWord != "":
            return int(sWord, 0x10)
        else:
            return "Error"

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
    def __GetHeaterOn(self, nReactor, sHeater):
        # Read the stop bit
        nWordOffset, nBitOffset = self.__LoopUpHeaterStop(nReactor, sHeater)
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

    # Get vacuum pressure
    def __GetVacuumPressure(self):
        nVacuumPLC = float(self.__GetAnalogValue("VacuumPressure"))
        return ((nVacuumPLC * self.__nVacuumGaugeSlope) + self.__nVacuumGaugeIntercept)

    # Get pressure regulator values
    def __GetPressureRegulatorSetPressure(self, nPressureRegulator):
        nPressurePLC = float(self.__GetAnalogValue("PressureRegulator" + str(nPressureRegulator) + "_SetPressure"))
        return ((nPressurePLC - self.__nPressureRegulatorSetIntercept) / self.__nPressureRegulatorSetSlope)
    def __GetPressureRegulatorActualPressure(self, nPressureRegulator):
        nPressurePLC = float(self.__GetAnalogValue("PressureRegulator" + str(nPressureRegulator) + "_ActualPressure"))
        return ((nPressurePLC * self.__nPressureRegulatorActualSlope) + self.__nPressureRegulatorActualIntercept)

    # Get radiation reading
    def __GetRadiation(self, nReactor):
        nRadiationPLC = float(self.__GetAnalogValue("Reactor" + str(nReactor) + "_RadiationDetector"))
        return ((nRadiationPLC - self.__nRadiationDetectorIntercept) / self.__nRadiationDetectorSlope)

    # Get reagent robot positions
    def __GetReagentRobotSetX(self):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__nReagentXAxis * 4)))
    def __GetReagentRobotSetZ(self):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__nReagentZAxis * 4)))
    def __GetReagentRobotActualX(self):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentXAxis * 4)))
    def __GetReagentRobotActualZ(self):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentZAxis * 4)))

    # Get reactor robot positions
    def __GetReactorRobotSetPosition(self, nReactor):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__LookUpReactorAxis(nReactor) * 4)))
    def __GetReactorRobotActualPosition(self, nReactor):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__LookUpReactorAxis(nReactor) * 4)))

    # Get the robot status
    def __GetRobotStatus(self, nAxis):
        nCheckWord = self.__GetIntegerValueRaw(ROBONET_CHECK + (nAxis * 4))
        if nCheckWord == ROBONET_INIT:
            return "Init"
        elif nCheckWord == ROBONET_SERVOON:
            return "On"
        elif nCheckWord == ROBONET_HOMING:
            return "Homing"
        elif nCheckWord == ROBONET_DISABLED:
            return "Disabled"
        elif (nCheckWord == ROBONET_ENABLED1) or (nCheckWord == ROBONET_ENABLED2):
            return "Enabled"
        elif nCheckWord == ROBONET_MOVING:
            return "Moving"
        elif (nCheckWord == ROBONET_ERROR1) or (nCheckWord == ROBONET_ERROR2) or (nCheckWord == ROBONET_ERROR3):
            return "Error"
        else:
            return str(nCheckWord)
    def __GetRobotControlWord(self, nReactor):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_CONTROL + (self.__LookUpReactorAxis(nReactor) * 4)))
    def __GetRobotCheckWord(self, nReactor):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_CHECK + (self.__LookUpReactorAxis(nReactor) * 4)))

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

    # Look up the reactor offset
    def __LookUpReactorOffset(self, nReactor):
        if (nReactor == 1):
            return self.__nReactor1ReactorOffset
        elif (nReactor == 2):
            return self.__nReactor2ReactorOffset
        elif (nReactor == 3):
            return self.__nReactor3ReactorOffset
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

    # Looks up the reagent robot position
    def __LookUpReagentRobotPosition(self, nPositionX, nPositionZ):
        # Hit test each reactor
        for nReactor in range(1,4):
            # Hit test each reagent position
            for nReagent in range(1, 11):
                pPosition = self.__LookUpRobotPosition("ReagentRobot_Reagent" + str(nReagent))
                nReagentXOffset = self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"])
                nReagentZOffset = self.__LookUpReactorCassetteZOffset(nReactor) + int(pPosition["z"])
                if self.__HitTest(nReagentXOffset, nPositionX) and self.__HitTest(nReagentZOffset, nPositionZ):
                  # We're over a reagent
                  return nReactor, nReagent, 0

            # Hit test each reagent delivery position
            for nReagentDelivery in range(1, 3):
                pPosition = self.__LookUpRobotPosition("ReagentRobot_ReagentDelivery" + str(nReagentDelivery))
                nReagentXOffset = self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"])
                nReagentZOffset = self.__LookUpReactorCassetteZOffset(nReactor) + int(pPosition["z"])
                if self.__HitTest(nReagentXOffset, nPositionX) and self.__HitTest(nReagentZOffset, nPositionZ):
                  # We're over a reagent delivery position
                  return nReactor, 0, nReagentDelivery
        
        # Failed to find match
        return 0, 0, 0
     
    # Look up the reactor robot position
    def __LookUpReactorRobotPosition(self, nPositionZ):
        # Hit test each reactor
        for nReactor in range(1,4):
            # Hit test each reactor position
            nReactorOffset = self.__LookUpReactorOffset(nReactor)
            for sPositionName in self.__pRobotPositions["Reactors"]:
                if self.__HitTest(nPositionZ, int(self.__pRobotPositions["Reactors"][sPositionName])):
                  # We're over a know position
                  return sPositionName
                  
        # Failed to find a named position
        return "Indeterminate" 

    # Hit tests the given reagent position
    def __HitTest(self, nPosition, nSetPosition):
        return ((nSetPosition - ROBOT_POSITION_LIMIT) <= nPosition) and ((nSetPosition + ROBOT_POSITION_LIMIT) >= nPosition)

    # Converts from an unsigned integer to a signed integer
    def __UnsignedToSigned(self, nUnsignedInt):
        # Is the MSB set?
        if nUnsignedInt & (1 << 15):
            # Yes, so this is a negative number.  Take the complement of the entire number
            nSignedInt = nUnsignedInt - 0xffff
        else:
            # No, so this is a positive number
            nSignedInt = nUnsignedInt

        # Return the signed integer
        return nSignedInt
