""" ElixysHardwareComm.py

Implements the HardwareComm interface for the Elixys hardware """

### Imports ###
from configobj import ConfigObj
from SocketThread import SocketThread
from SocketThread import RunawayHeaterException
import threading
import time
import os
import sys


import logging

log = logging.getLogger("elixys.hw")
flog = logging.getLogger("elixys.plc")
log.info("Starting HW Comm")


### Constants ###

# IP and port of the PLC.  Make sure only one PLC IP is defined
REAL_PLC_IP = "192.168.1.200"    # Real PLC
log.debug("PLC IP: %s" % REAL_PLC_IP)
FAKE_PLC_IP = "127.0.0.1"        # Fake PLC for testing and demo
log.debug("FAKE PLC IP: %s" % FAKE_PLC_IP)
PLC_PORT = 9600
log.debug("PLC Port: %s" % FAKE_PLC_IP)

# Number of words used by each type of module
DIGITALOUT_SIZE = 0x4
DIGITALIN_SIZE = 0x1
ANALOGOUT_SIZE = 0xa
ANALOGIN_SIZE = 0xa
THERMOCONTROLLER_SIZE = 0x14
DEVICENET_SIZE = 0x19

# RoboNet addresses
ROBONET_MIN = 3201
ROBONET_MAX = 3312 + (5 * 4)
ROBONET_ENABLE = 3201
ROBONET_CONTROL = 3212
ROBONET_AXISPOSSET = 3209
ROBONET_AXISPOSREAD = 3309
ROBONET_ERROR = 3311
ROBONET_CHECK = 3312

# RoboNet status offsets
ROBONET_STATUS_HOMECOMPLETE = 1
ROBONET_STATUS_MOVING = 2
ROBONET_STATUS_ALARM = 3
ROBONET_STATUS_READY = 4

# FakePLC RoboNet status values
FAKEPLC_ROBONET_HOMING = (1 << ROBONET_STATUS_READY) | (1 << ROBONET_STATUS_MOVING)
FAKEPLC_ROBONET_ENABLED = (1 << ROBONET_STATUS_READY)
FAKEPLC_ROBONET_DISABLED = (1 << ROBONET_STATUS_HOMECOMPLETE)

# Robot position hit test limit
ROBOT_POSITION_LIMIT = 150

# State update timeout in seconds and max retry count
STATE_UPDATE_TIMEOUT = 3
STATE_UPDATE_TIMEOUT_COUNT = 3

# Liquid sensor threshold
LIQUID_SENSOR_THRESHOLD = 1000

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

    def __init__(self):
        # Load the hardware map and robot positions
        sHardwareMap = "/opt/elixys/hardware/HardwareMap.ini"
        sRobotPositions = "/opt/elixys/hardware/RobotPositions.ini"
        if not os.path.exists(sHardwareMap):
            raise Exception("Hardware map INI file not found")
        if not os.path.exists(sRobotPositions):
            raise Exception("Robot positions INI file not found")
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
        self.__nReagentYAxis = int(self.__pRobotPositions["ReagentYAxis"])
        self.__nReactor1Axis = int(self.__pRobotPositions["Reactor1Axis"])
        self.__nReactor2Axis = int(self.__pRobotPositions["Reactor2Axis"])
        self.__nReactor3Axis = int(self.__pRobotPositions["Reactor3Axis"])

        # Load the reactor offsets
        self.__nReactor1CassetteXOffset = int(self.__pRobotPositions["Reactor1"]["CassetteXOffset"])
        self.__nReactor1CassetteYOffset = int(self.__pRobotPositions["Reactor1"]["CassetteYOffset"])
        self.__nReactor1ReactorOffset = int(self.__pRobotPositions["Reactor1"]["ReactorOffset"])
        self.__nReactor2CassetteXOffset = int(self.__pRobotPositions["Reactor2"]["CassetteXOffset"])
        self.__nReactor2CassetteYOffset = int(self.__pRobotPositions["Reactor2"]["CassetteYOffset"])
        self.__nReactor2ReactorOffset = int(self.__pRobotPositions["Reactor2"]["ReactorOffset"])
        self.__nReactor3CassetteXOffset = int(self.__pRobotPositions["Reactor3"]["CassetteXOffset"])
        self.__nReactor3CassetteYOffset = int(self.__pRobotPositions["Reactor3"]["CassetteYOffset"])
        self.__nReactor3ReactorOffset = int(self.__pRobotPositions["Reactor3"]["ReactorOffset"])

        # Calculate the memory address range.  We will use this information to query for the entire state at once
        self.__nMemoryLower, self.__nMemoryUpper = self.CalculateMemoryRange()

        # Initialize our variables
        self.__pSystemModel = None
        self.__nStateOffset = 0
        self.__sState = ""
        self.__bLoadingState = False
        self.__nLoadStateStart = 0
        self.__nLoadTimeoutCount = 0
        self.__pThermocontrollerDecimalPointFlags = {}
        self.__sLogFile = ""
        self.__startTime = 0
        self.__bTempLogging = False
        self.__FakePLC_pMemory = None
        self.__FakePLC_nMemoryLower = 0
        self.__FakePLC_nMemoryUpper = 0
        self.__FakePLC_nHomingReagentRobotXStep = 0
        self.__FakePLC_nHomingReagentRobotYStep = 0
        self.__FakePLC_nHomingReactorRobot1Step = 0
        self.__FakePLC_nHomingReactorRobot2Step = 0
        self.__FakePLC_nHomingReactorRobot3Step = 0
        
    ### Public functions ###

    def StartUp(self):
        log.info("Connecting to PLC")
        # Determine the PLC IP
        sDemoFile = "/opt/elixys/demomode"
        if not os.path.isfile(sDemoFile):
            nPLC_IP = REAL_PLC_IP
            log.info("Using Real PLC")
        else:
            nPLC_IP = FAKE_PLC_IP
            log.info("Using Fake PLC")

        # Spawn the socket thread
        self.__pSocketThread = SocketThread()
        self.__pSocketThreadTerminateEvent = threading.Event()
        self.__pSocketThread.SetParameters(nPLC_IP, PLC_PORT, self, 
                self.__pSocketThreadTerminateEvent)
        self.__pSocketThread.setDaemon(True)
        self.__pSocketThread.start()

    def ShutDown(self):
        # Stop the socket thread
        log.debug("Shutdown PLC Connection")
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
        if not self.IsFakePLC():
            # We are in normal mode.  Make sure the socket thread is alive and well
            if self.__pSocketThread == None:
                log.error("Hardware Thread does not exist")
                raise Exception("Socket thread does not exist")
            if self.__pSocketThread.GetError() != "":
                raise Exception(self.__pSocketThread.GetError())
            if not self.__pSocketThread.is_alive():
                log.error("Hardware Thread quit unexpectedly")
                raise Exception("Socket thread terminated unexpectedly")

            # Are we already in the processes of updating the state?
            if self.__bLoadingState:
                # Yes, so check if we have timed out
                if (time.time() - self.__nLoadStateStart) < STATE_UPDATE_TIMEOUT:
                    # We haven't timed out yet
                    return
                else:
                    # We've timed out
                    if (self.__nLoadTimeoutCount < STATE_UPDATE_TIMEOUT_COUNT):
                        # Recycle the connection and request the state again
                        self.ShutDown()
                        self.StartUp()
                        self.__nLoadTimeoutCount += 1
                    else:
                        raise Exception("Failed to communicate with PLC")

            # We're limited in the maximum amount of data we can read in a single request.  Start by requesting the
            # first chunk of the state
            self.__nStateOffset = self.__nMemoryLower
            self.__sState = ""
            self.__bLoadingState = True
            self.__nLoadStateStart = time.time()
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

    # Determines if we are using a fake PLC
    def IsFakePLC(self):
      return (self.__FakePLC_pMemory != None)

    ### Hardware control functions ###

    # Cooling system
    def CoolingSystemOn(self):
        log.debug("Cooling System On")
        self.__SetBinaryValue("CoolingSystemOn", True)
    def CoolingSystemOff(self):
        log.debug("Cooling System Off")
        self.__SetBinaryValue("CoolingSystemOn", False)
    
    # Vacuum system (currently not implemented in the hardware)
    def VacuumSystemOn(self):
        log.debug("Vaccuum System On")
        self.__SetBinaryValue("VacuumSystemOn", True)
    def VacuumSystemOff(self):
        log.debug("Vacuum System Off")
        self.__SetBinaryValue("VacuumSystemOn", False)

    # Pressure regulator
    def SetPressureRegulator(self, nPressureRegulator, nPressurePSI):
        nPressurePLC = (nPressurePSI * self.__nPressureRegulatorSetSlope) + self.__nPressureRegulatorSetIntercept
	log.debug("SetPressureRegulator:nPress: %d,nPSI:%f,nPLC:%f" 
			% (nPressureRegulator, nPressurePSI,nPressurePLC))        
	if nPressurePLC < 0:
            nPressurePLC = 0
        if nPressurePLC > 4200:
            nPressurePLC = 4200
        self.__SetIntegerValue("PressureRegulator" + str(nPressureRegulator) + "_SetPressure", nPressurePLC)

    # Reagent robot
    def MoveRobotToElute(self, nReactor):
        log.debug("Move Robot and Elute - Reactor %d" % nReactor)
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["ReagentDelivery"].getCurrentGripperUp() or \
               not self.__pSystemModel.model["ReagentDelivery"].getCurrentGasTransferUp():
                raise Exception("Cannot move reagent robot unless gripper and gas transfer are up")
        pPosition = self.__LookUpRobotPosition("ReagentRobot_Elute")
        self.__SetRobotPosition(self.__nReagentXAxis, self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"]))
        self.__SetRobotPosition(self.__nReagentYAxis, self.__LookUpReactorCassetteYOffset(nReactor) + int(pPosition["y"]))
    def MoveRobotToReagent(self, nReactor, nReagent):
        log.info("Move Robot to Reagent:Reactor %d->Reagent %d" % (nReactor,nReagent))
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["ReagentDelivery"].getCurrentGripperUp() or \
               not self.__pSystemModel.model["ReagentDelivery"].getCurrentGasTransferUp():
                raise Exception("Cannot move reagent robot unless gripper and gas transfer are up")
        pPosition = self.__LookUpRobotPosition("ReagentRobot_Reagent" + str(nReagent))
        self.__SetRobotPosition(self.__nReagentXAxis, self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"]))
        self.__SetRobotPosition(self.__nReagentYAxis, self.__LookUpReactorCassetteYOffset(nReactor) + int(pPosition["y"]))
    def MoveRobotToDelivery(self, nReactor, nPosition):
        log.info("Move Robot & Deliver:Reactor %d->Position %d" % (nReactor,nPosition))
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["ReagentDelivery"].getCurrentGripperUp() or \
               not self.__pSystemModel.model["ReagentDelivery"].getCurrentGasTransferUp():
                raise Exception("Cannot move reagent robot unless gripper and gas transfer are up")
        pPosition = self.__LookUpRobotPosition("ReagentRobot_ReagentDelivery" + str(nPosition))
        self.__SetRobotPosition(self.__nReagentXAxis, self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"]))
        self.__SetRobotPosition(self.__nReagentYAxis, self.__LookUpReactorCassetteYOffset(nReactor) + int(pPosition["y"]))
    def MoveRobotToHome(self):
        log.debug("Move Robot Home")
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["ReagentDelivery"].getCurrentGripperUp() or \
               not self.__pSystemModel.model["ReagentDelivery"].getCurrentGasTransferUp():
                raise Exception("Cannot move reagent robot unless gripper and gas transfer are up")
        self.__SetRobotPosition(self.__nReagentXAxis, 0)
        self.__SetRobotPosition(self.__nReagentYAxis, 0)
    def MoveRobotToX(self, nX):
        log.info("Move to X: %d" % nX)
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["ReagentDelivery"].getCurrentGripperUp() or \
               not self.__pSystemModel.model["ReagentDelivery"].getCurrentGasTransferUp():
                raise Exception("Cannot move reagent robot unless gripper and gas transfer are up")
        self.__SetRobotPosition(self.__nReagentXAxis, int(nX))
    def MoveRobotToY(self, nY):
        log.info("Move to Y: %d" % nY)
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["ReagentDelivery"].getCurrentGripperUp() or \
               not self.__pSystemModel.model["ReagentDelivery"].getCurrentGasTransferUp():
                raise Exception("Cannot move reagent robot unless gripper and gas transfer are up")
        self.__SetRobotPosition(self.__nReagentYAxis, int(nY))
    def GripperUp(self):
        log.debug("Gripper Up")
        self.__SetBinaryValue("ReagentRobot_SetGripperDown", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", True)
    def GripperDown(self):
        log.debug("Gripper Down")
        self.__SetBinaryValue("ReagentRobot_SetGripperUp", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperDown", True)
    def GripperOpen(self):
        log.debug("Gripper Open")
        self.__SetBinaryValue("ReagentRobot_SetGripperClose", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", True)
    def GripperClose(self):
        log.debug("Gripper Close")
        self.__SetBinaryValue("ReagentRobot_SetGripperOpen", False)
        self.__SetBinaryValue("ReagentRobot_SetGripperClose", True)
    def GasTransferUp(self):
        log.debug("Gas Transfer Up")
        self.__SetBinaryValue("ReagentRobot_SetGasTransferDown", False)
        self.__SetBinaryValue("ReagentRobot_SetGasTransferUp", True)
    def GasTransferDown(self):
        log.debug("Gas Transfer Down")
        self.__SetBinaryValue("ReagentRobot_SetGasTransferUp", False)
        self.__SetBinaryValue("ReagentRobot_SetGasTransferDown", True)

    # Valves
    def GasTransferStart(self):
        log.info("Gase Transfer Start")
        self.__SetBinaryValue("Valves_GasTransferValve", True)
    def GasTransferStop(self):
        log.info("Gas Transfer Stop")
        self.__SetBinaryValue("Valves_GasTransferValve", False)
    def LoadF18Start(self):
        log.debug("Load F18")
        self.__SetBinaryValue("Valves_F18Load", True)
    def LoadF18Stop(self):
        log.debug("Stop F18")
        self.__SetBinaryValue("Valves_F18Load", False)
    def HPLCLoad(self):
        log.debug("Load HPLC")
        self.__SetBinaryValue("Valves_HPLCInject", False)
    def HPLCInject(self):
        log.debug("Inject HPLC")
        self.__SetBinaryValue("Valves_HPLCInject", True)

    # Reactor
    def MoveReactor(self, nReactor, sPositionName):
        log.debug("Move Reactor %d to %s" % (nReactor, sPositionName))
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentReactorDown():
                raise Exception("Cannot move reactor robot unless reactor is down")
        nReactorOffset = self.__LookUpReactorOffset(nReactor)
        pPosition = self.__LookUpRobotPosition("Reactors_" + sPositionName)
        self.__SetRobotPosition(self.__LookUpReactorAxis(nReactor), nReactorOffset + int(pPosition["y"]))
    def ReactorUp(self, nReactor):
        log.debug("Reactor %d Up" % nReactor)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorDown", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorUp", True)
    def ReactorDown(self, nReactor):
        log.debug("Reactor %d Down" % nReactor)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorUp", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_SetReactorDown", True)
    def ReactorStopcockCW(self, nReactor, nStopcock):
        log.debug("Reactor %d stopcock %d CW" % (nReactor,nStopcock))
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + 
                str(nStopcock) + "ValveCCW", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + 
                str(nStopcock) + "ValveCW", True)
    def ReactorStopcockCCW(self, nReactor, nStopcock):
        log.debug("Reactor %d stopcock %d CCW" % (nReactor,nStopcock))
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValveCW", False)
        time.sleep(0.1)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_Stopcock" + str(nStopcock) + "ValveCCW", True)

    # Temperature controllers
    def HeaterOn(self, nReactor):
        log.debug("Heater On Reactor %d" % nReactor)
        # Clear the stop bit
        for nHeater in range(1, 4):
            self.SingleHeaterOn(nReactor, nHeater)
    def HeaterOff(self, nReactor):
        log.debug("Heater Off Reactor %d" % nReactor)
        # Set the stop bit
        for nHeater in range(1, 4):
            self.SingleHeaterOff(nReactor, nHeater)
    def SingleHeaterOn(self, nReactor, nHeater):
        log.debug("Single Heater %d On -> Reactor %d" % (nHeater,nReactor))
        # Clear the stop bit
        nWordOffset, nBitOffset = self.__LoopUpHeaterStop(nReactor, nHeater)
        self.__SetBinaryValueRaw(nWordOffset, nBitOffset, 0)
    def SingleHeaterOff(self, nReactor, nHeater):
        log.debug("Single Heater %d Off -> Reactor %d" % (nHeater,nReactor))
        # Set the stop bit
        nWordOffset, nBitOffset = self.__LoopUpHeaterStop(nReactor, nHeater)
        self.__SetBinaryValueRaw(nWordOffset, nBitOffset, 1)
    def SetHeaterTemp(self, nReactor, nSetPoint):
        # Set the heater temperature
        log.debug("Set Reactor %d Heater Temp %f" % (nReactor, nSetPoint)) 
        for nHeater in range(1, 4):
            self.__SetThermocontrollerSetValue("Reactor" + str(nReactor) + "_TemperatureController" + str(nHeater), nSetPoint)

    # Stir motor
    def SetMotorSpeed(self, nReactor, nMotorSpeed):
        log.debug("Set Reactor %d motor speed: %d" % (nReactor, nMotorSpeed))
        self.__SetIntegerValue("Reactor" + str(nReactor) + "_StirMotor", nMotorSpeed)

    # Home all robots
    def HomeRobots(self):
        # Home the reactors and reagent robots
        log.debug("Home Robots")
        self.HomeReactorRobots()
        self.HomeReagentRobots()

    # Home the reactor robots
    def HomeReactorRobots(self):
        log.debug("Home Reactor Robots")
        for nReactor in range(1,4):
            self.HomeReactorRobot(nReactor)
    def HomeReactorRobot(self, nReactor):
        log.debug("Home Reactor %d Robot" % nReactor)
        # Make sure the reactor is down
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentReactorDown():
                raise Exception("Cannot home reactor robot unless reactor is down")

        # Set the reactor position to install before homing
        self.MoveReactor(nReactor, "Install")

        # Turn on the reactor axis
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__LookUpReactorAxis(nReactor) * 4), 0x10)
        time.sleep(0.1)

        # Home the axis
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__LookUpReactorAxis(nReactor) * 4), 0x12)
        time.sleep(0.1)

    # Home the reagent robots
    def HomeReagentRobots(self):
        # Make sure the gripper and gas transfer arms are up
        log.debug("Home Reagent Robots")
        if self.__pSystemModel != None:
            if not self.__pSystemModel.model["ReagentDelivery"].getCurrentGripperUp() or \
               not self.__pSystemModel.model["ReagentDelivery"].getCurrentGasTransferUp():
                raise Exception("Cannot home reagent robot unless gripper and gas transfer are up")

        # Turn on and home the X axis
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentXAxis * 4), 0x10)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentXAxis * 4), 0x12)
        time.sleep(0.1)

        # Turn on and home the Y axis
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentYAxis * 4), 0x10)
        time.sleep(0.1)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentYAxis * 4), 0x12)
        time.sleep(0.1)

    # Disable all robots
    def DisableRobots(self):
        log.debug("Disable Robots")
        self.DisableReagentRobots()
        time.sleep(0.1)
        for nReactor in range(1, 4):
            # Disable each axis
            self.DisableReactorRobot(nReactor)
            time.sleep(0.1)
        
    # Enable all robots
    def EnableRobots(self):
        log.info("Enable Robots")
        self.EnableReagentRobots()
        time.sleep(0.1)
        for nReactor in range(1, 4):
            # Enable each axis
            self.EnableReactorRobot(nReactor)
            time.sleep(0.1)

    # Disable reagent robots
    def DisableReagentRobots(self):
        log.info("Disable Reagent Robots")
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentXAxis * 4), 0x08)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentYAxis * 4), 0x08)

    # Enable reagent robots
    def EnableReagentRobots(self):
        log.debug("Enable Reagent Robots")
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentXAxis * 4), 0x10)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__nReagentYAxis * 4), 0x10)

    # Disable reactor robot
    def DisableReactorRobot(self, nReactor):
        log.debug("Disable Reactor Robot %d" % nReactor)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__LookUpReactorAxis(nReactor) * 4), 0x08)

    # Enable reactor robot
    def EnableReactorRobot(self, nReactor):
        log.debug("Enable Reactor Robot %d" % nReactor)
        self.__SetIntegerValueRaw(ROBONET_CONTROL + (self.__LookUpReactorAxis(nReactor) * 4), 0x10)

    # Begin logging temperatures
    def StartTempLogging(self):
        log.debug("Start Temp Logging")
        self.__StartTempLogging()

    # Stops logging temperatures
    def StopTempLogging(self):
        log.debug("Stop Temp Logging")
        self.__StopTempLogging()

    ### Fake PLC functions ###
    
    # Used by the fake PLC to set the PLC memory
    def FakePLC_SetMemory(self, pMemory, nMemoryLower, nMemoryUpper):
        # Make sure the memory ranges match up
        #flog.debug("Fake PLC Set Memory (%d,%d)" % (nMemoryLower, nMemoryUpper))
        if (nMemoryLower != self.__nMemoryLower) or (nMemoryUpper != self.__nMemoryUpper):
            raise Exception("Memory range mismatch")

        # Remember the memory and range
        self.__FakePLC_pMemory = pMemory
        self.__FakePLC_nMemoryLower = nMemoryLower
        self.__FakePLC_nMemoryUpper = nMemoryUpper

    # Used by the fake PLC to read back a range of the fake memory
    def FakePLC_ReadMemory(self, nReadOffset, nReadLength):
        #flog.debug("Fake PLC Read Memory (%d,%d)" % (nReadOffset, nReadLength))
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
        #flog.debug("FAKE:Set Vacuum Pressure %d" % nPressure)
        nPressurePLC = (nPressure - self.__nVacuumGaugeIntercept) / self.__nVacuumGaugeSlope
        self.__SetIntegerValue("VacuumPressure", nPressurePLC)
    def FakePLC_SetPressureRegulatorActualPressure(self, nPressureRegulator, nPressure):
        flog.debug("FAKE:Set Pressure Regulator %d -> %f" % (nPressureRegulator,nPressure))
        nPressurePLC = (nPressure - self.__nPressureRegulatorActualIntercept) / self.__nPressureRegulatorActualSlope
        self.__SetIntegerValue("PressureRegulator" + str(nPressureRegulator) + "_ActualPressure", nPressurePLC)
    def FakePLC_SetReagentRobotSetPosition(self, nPositionX, nPositionZ):
        #flog.debug("FAKE:Set Reagent Robot Position->X%d,Y%d" % (nPositionX,nPositionZ))
        self.__SetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__nReagentXAxis * 4), nPositionX)
        self.__SetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__nReagentYAxis * 4), nPositionZ)
    def FakePLC_SetReagentRobotActualPosition(self, nPositionX, nPositionZ):
        #flog.debug("FAKE:Set Reagent Robot Actual Position->X%d,Y%d" % 
        #        (nPositionX,nPositionZ))
        self.__SetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentXAxis * 4), nPositionX)
        self.__SetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentYAxis * 4), nPositionZ)
    def FakePLC_SetReagentRobotGripper(self, bGripperUp, bGripperDown, bGripperOpen, bGripperClose, bGasTransferUp, bGasTransferDown):
        self.__SetBinaryValue("ReagentRobot_GripperUp", bGripperUp)
        self.__SetBinaryValue("ReagentRobot_GripperDown", bGripperDown)
        self.__SetBinaryValue("ReagentRobot_GripperOpen", bGripperOpen)
        self.__SetBinaryValue("ReagentRobot_GripperClose", bGripperClose)
        self.__SetBinaryValue("ReagentRobot_GasTransferUp", bGasTransferUp)
        self.__SetBinaryValue("ReagentRobot_GasTransferDown", bGasTransferDown)
    def FakePLC_CheckForHomingReagentRobotX(self):
        #flog.debug("Check Homing Reagent Robot X")
        return (self.__FakePLC_nHomingReagentRobotXStep == 2)
    def FakePLC_CheckForHomingReagentRobotY(self):
        #flog.info("Check for Homing Reagent Y")
        return (self.__FakePLC_nHomingReagentRobotYStep == 2)
    def FakePLC_CheckForHomingReactorRobot(self, nReactor):
        #flog.info("Check for Homing Reactor Robot %d" % nReactor)
        if nReactor == 1:
            return (self.__FakePLC_nHomingReactorRobot1Step == 2)
        elif nReactor == 2:
            return (self.__FakePLC_nHomingReactorRobot2Step == 2)
        elif nReactor == 3:
            return (self.__FakePLC_nHomingReactorRobot3Step == 2)
        else:
            raise Exception("Invalid reactor")
    def FakePLC_ResetReagentRobotHoming(self):
        #flog.debug("Reset Reagent Robot Homing")
        self.__FakePLC_nHomingReagentRobotXStep = 0
        self.__FakePLC_nHomingReagentRobotYStep = 0
    def FakePLC_ResetReactorRobotHoming(self, nReactor):
        #flog.debug("Reset Reactor Robot Homing")
        if nReactor == 1:
            self.__FakePLC_nHomingReactorRobot1Step = 0
        elif nReactor == 2:
            self.__FakePLC_nHomingReactorRobot2Step = 0
        elif nReactor == 3:
            self.__FakePLC_nHomingReactorRobot3Step = 0
        else:
            raise Exception("Invalid reactor")
    def FakePLC_HomeReagentRobotX(self):
        #flog.debug("Home Reagent Robot X")
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__nReagentXAxis * 4), FAKEPLC_ROBONET_HOMING)
    def FakePLC_HomeReagentRobotY(self):
        #flog.debug("Home Reagent Robot Y")
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__nReagentYAxis * 4), FAKEPLC_ROBONET_HOMING)
    def FakePLC_HomeReactorRobot(self, nReactor):
        #flog.debug("Home Reactor Robot %d" % nReactor)
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__LookUpReactorAxis(nReactor) * 4), FAKEPLC_ROBONET_HOMING)
    def FakePLC_EnableReagentRobotX(self):
        #flog.debug("Enable Reagent Robot X")
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__nReagentXAxis * 4), FAKEPLC_ROBONET_ENABLED)
    def FakePLC_DisableReagentRobotX(self):
        #flog.info("Disable Reagent Robot X")
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__nReagentXAxis * 4), FAKEPLC_ROBONET_DISABLED)
    def FakePLC_EnableReagentRobotY(self):
        #flog.debug("Enable Reagent Robot Y")
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__nReagentYAxis * 4), FAKEPLC_ROBONET_ENABLED)
    def FakePLC_DisableReagentRobotY(self):
        #flog.debuge("Disable Reagent Robot Y")
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__nReagentYAxis * 4), FAKEPLC_ROBONET_DISABLED)
    def FakePLC_EnableReactorRobot(self, nReactor):
        #flog.debug("Enable Reactor Robot %d" % nReactor)
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__LookUpReactorAxis(nReactor) * 4), FAKEPLC_ROBONET_ENABLED)
    def FakePLC_DisableReactorRobot(self, nReactor):
        #flog.debug("Disable Reactor Robot %d" % nReactor)
        self.__SetIntegerValueRaw(ROBONET_CHECK + (self.__LookUpReactorAxis(nReactor) * 4), FAKEPLC_ROBONET_DISABLED)
    def FakePLC_SetReactorLinearSetPosition(self, nReactor, nPositionY):
        #flog.debug("Move Reactor %d to Y Pos %d" % (nReactor, nPositionY))
        self.__SetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__LookUpReactorAxis(nReactor) * 4), nPositionY)
    def FakePLC_SetReactorLinearActualPosition(self, nReactor, nPositionY):
        #flog.debug("Move Reactor %d to actuatl Y Pos %d" % (nReactor, nPositionY))
        self.__SetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__LookUpReactorAxis(nReactor) * 4), nPositionY)
    def FakePLC_SetReactorVerticalPosition(self, nReactor, bUpSensor, bDownSensor):
        #flog.debug("Set Reactor %d Vertical Position UP:%s,DOWN:%s" 
        #        % (nReactor,bUpSensor,bDownSensor))
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_ReactorUp", bUpSensor)
        self.__SetBinaryValue("Reactor" + str(nReactor) + "_ReactorDown", bDownSensor)
    def FakePLC_SetReactorActualTemperature(self, nReactor, nHeater, nTemperature):
        #flog.debug("Set Reactor %d heater %d Actual Temperature %d"  
        #        % (nReactor,nHeater,nTemperature))
        nOffset = self.__LookUpThermocontrollerActualOffset("Reactor" + str(nReactor) + "_TemperatureController" + str(nHeater))
        self.__SetIntegerValueRaw(nOffset, nTemperature)
    def FakePLC_SetBinaryValue(self, nWordOffset, nBitOffset, bValue):
        self.__SetBinaryValueRaw(nWordOffset, nBitOffset, bValue)
    def FakePLC_SetWordValue(self, nWordOffset, nValue):
        # Watch for the memory toggle that signals the robots to home
        if (self.__FakePLC_nHomingReagentRobotXStep == 0) and (nWordOffset == (ROBONET_CONTROL + (self.__nReagentXAxis * 4))) and (nValue == 0x10):
            self.__FakePLC_nHomingReagentRobotXStep = 1
        if (self.__FakePLC_nHomingReagentRobotXStep == 1) and (nWordOffset == (ROBONET_CONTROL + (self.__nReagentXAxis * 4))) and (nValue == 0x12):
            self.__FakePLC_nHomingReagentRobotXStep = 2
        if (self.__FakePLC_nHomingReagentRobotYStep == 0) and (nWordOffset == (ROBONET_CONTROL + (self.__nReagentYAxis * 4))) and (nValue == 0x10):
            self.__FakePLC_nHomingReagentRobotYStep = 1
        if (self.__FakePLC_nHomingReagentRobotYStep == 1) and (nWordOffset == (ROBONET_CONTROL + (self.__nReagentYAxis * 4))) and (nValue == 0x12):
            self.__FakePLC_nHomingReagentRobotYStep = 2
        if (self.__FakePLC_nHomingReactorRobot1Step == 0) and (nWordOffset == (ROBONET_CONTROL + (self.__LookUpReactorAxis(1) * 4))) and (nValue == 0x10):
            self.__FakePLC_nHomingReactorRobot1Step = 1
        if (self.__FakePLC_nHomingReactorRobot1Step == 1) and (nWordOffset == (ROBONET_CONTROL + (self.__LookUpReactorAxis(1) * 4))) and (nValue == 0x12):
            self.__FakePLC_nHomingReactorRobot1Step = 2
        if (self.__FakePLC_nHomingReactorRobot2Step == 0) and (nWordOffset == (ROBONET_CONTROL + (self.__LookUpReactorAxis(2) * 4))) and (nValue == 0x10):
            self.__FakePLC_nHomingReactorRobot2Step = 1
        if (self.__FakePLC_nHomingReactorRobot2Step == 1) and (nWordOffset == (ROBONET_CONTROL + (self.__LookUpReactorAxis(2) * 4))) and (nValue == 0x12):
            self.__FakePLC_nHomingReactorRobot2Step = 2
        if (self.__FakePLC_nHomingReactorRobot3Step == 0) and (nWordOffset == (ROBONET_CONTROL + (self.__LookUpReactorAxis(3) * 4))) and (nValue == 0x10):
            self.__FakePLC_nHomingReactorRobot3Step = 1
        if (self.__FakePLC_nHomingReactorRobot3Step == 1) and (nWordOffset == (ROBONET_CONTROL + (self.__LookUpReactorAxis(3) * 4))) and (nValue == 0x12):
            self.__FakePLC_nHomingReactorRobot3Step = 2

        # Set the raw value
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
        if not self.IsFakePLC():
            # We are in normal mode.  Format and send the raw command to the PLC
            sCommand = "010230"                                 # Write bit to CIO memory
            sCommand = sCommand + ("%0.4X" % nWordOffset)       # Memory offset (words)
            sCommand = sCommand + ("%0.2X" % nBitOffset)        # Memory offset (bits)
            sCommand = sCommand + "0001"                        # Number of bits to write
            if bValue:
                sCommand = sCommand + "01"                      # Set bit
            else:
                sCommand = sCommand + "00"                      # Clear bit
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
                self.__FakePLC_pMemory[nWordOffset] = int(self.__FakePLC_pMemory[nWordOffset]) & ~(1 << nBitOffset)

    # Set integer value by hardware name
    def __SetIntegerValue(self, sHardwareName, nValue):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calculate the absolute address of the target word
        nAbsoluteWordOffset = self.__DetermineHardwareOffset(pHardware) + int(pHardware["location"])
        
        # Set the integer value
        self.__SetIntegerValueRaw(nAbsoluteWordOffset, int(nValue))

    # Set integer value raw
    def __SetIntegerValueRaw(self, nAddress, nValue):
        # What mode are we in?
        if not self.IsFakePLC():
            # We are in normal mode.  Format and send the raw command to the PLC
            sCommand = "0102B0"	                                    # Write word to CIO memory
            sCommand = sCommand + ("%0.4X" % nAddress)              # Memory offset (words)
            sCommand = sCommand + "00"                              # Memory offset (bits)
            sCommand = sCommand + "0001"                            # Number of words to write
            sCommand = sCommand + ("%0.4X" % nValue)                # Set word
            self.__SendRawCommand(sCommand)
        else:
            # We are in fake PLC mode.  Validate the address
            if (nAddress < self.__FakePLC_nMemoryLower) or ((nAddress + self.__FakePLC_nMemoryLower) >= self.__FakePLC_nMemoryUpper):
                raise Exception("Invalid word offset")
            
            # Update the target word in the fake memory
            self.__FakePLC_pMemory[nAddress] = nValue

    # Set thermocontroller value
    def __SetThermocontrollerSetValue(self, sHardwareName, fValue):
        # Look up the temperature set offset and set the value
        nOffset = self.__LookUpThermocontrollerSetOffset(sHardwareName)
        if self.__GetThermocontrollerDecimalPoint(sHardwareName):
            fValue *= 10
        self.__SetIntegerValueRaw(nOffset, int(fValue))

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

        # Clear our state loading flag and reset our timeout counter
        self.__bLoadingState = False
        self.__nLoadTimeoutCount = 0

        # Enable analog out as needed
        nAnalogOutOffset = self.__CalculateHardwareOffset(self.__nAnalogOutUnit);
        if self.__GetIntegerValueRaw(nAnalogOutOffset) != 0xFF:
            self.__SetIntegerValueRaw(nAnalogOutOffset, 0xFF);
        
        # Enable RoboNet control for all axes as needed
        if self.__GetIntegerValueRaw(ROBONET_ENABLE) != 0x8000:
            self.__SetIntegerValueRaw(ROBONET_ENABLE, 0x8000)

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
            # Check for runaway reactor temperatures
            for nReactor in range(1, 4):
                for nTemperatureController in range(1, 4):
                    self.__CheckForRunawayTemp(nReactor, nTemperatureController)
            
            # Look up our reagent robot positions
            nReagentRobotSetX = self.__GetReagentRobotSetX()
            nReagentRobotSetY = self.__GetReagentRobotSetY()
            nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery, nReagentRobotSetPositionElute = \
                self.__LookUpReagentRobotPosition(nReagentRobotSetX, nReagentRobotSetY)
            nReagentRobotActualX = self.__GetReagentRobotActualX()
            nReagentRobotActualY = self.__GetReagentRobotActualY()
            nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery, nReagentRobotCurrentPositionElute = \
                self.__LookUpReagentRobotPosition(nReagentRobotActualX, nReagentRobotActualY)

            # Look up our reactor robot positions
            nReactor1RobotSetPositionRaw = self.__GetReactorRobotSetPosition(1)
            nReactor1RobotActualPositionRaw = self.__GetReactorRobotActualPosition(1)
            nReactor1RobotSetPosition = self.__LookUpReactorRobotPosition(1, nReactor1RobotSetPositionRaw)
            nReactor1RobotActualPosition = self.__LookUpReactorRobotPosition(1, nReactor1RobotActualPositionRaw)
            nReactor2RobotSetPositionRaw = self.__GetReactorRobotSetPosition(2)
            nReactor2RobotActualPositionRaw = self.__GetReactorRobotActualPosition(2)
            nReactor2RobotSetPosition = self.__LookUpReactorRobotPosition(2, nReactor2RobotSetPositionRaw)
            nReactor2RobotActualPosition = self.__LookUpReactorRobotPosition(2, nReactor2RobotActualPositionRaw)
            nReactor3RobotSetPositionRaw = self.__GetReactorRobotSetPosition(3)
            nReactor3RobotActualPositionRaw = self.__GetReactorRobotActualPosition(3)
            nReactor3RobotSetPosition = self.__LookUpReactorRobotPosition(3, nReactor3RobotSetPositionRaw)
            nReactor3RobotActualPosition = self.__LookUpReactorRobotPosition(3, nReactor3RobotActualPositionRaw)

            # Update the system model
            pModel["CoolingSystem"].updateState(self.__GetBinaryValue("CoolingSystemOn"))
            pModel["VacuumSystem"].updateState(self.__GetBinaryValue("VacuumSystemOn"), self.__GetVacuumPressure())
            pModel["Valves"].updateState(self.__GetBinaryValue("Valves_GasTransferValve"), self.__GetBinaryValue("Valves_F18Load"), self.__GetBinaryValue("Valves_HPLCInject"))
            pModel["LiquidSensors"].updateState(self.__GetLiquidSensor(1), self.__GetLiquidSensor(2), self.__GetLiquidSensorRaw(1), self.__GetLiquidSensorRaw(2))
            pModel["PressureRegulator1"].updateState(self.__GetPressureRegulatorSetPressure(1), self.__GetPressureRegulatorActualPressure(1))
            pModel["PressureRegulator2"].updateState(self.__GetPressureRegulatorSetPressure(2), self.__GetPressureRegulatorActualPressure(2))
            pModel["ReagentDelivery"].updateState(nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery,
                nReagentRobotSetPositionElute, nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery,
                nReagentRobotCurrentPositionElute, nReagentRobotSetX, nReagentRobotSetY, nReagentRobotActualX, nReagentRobotActualY, 
                self.__GetBinaryValue("ReagentRobot_SetGripperUp"), self.__GetBinaryValue("ReagentRobot_SetGripperDown"), 
                self.__GetBinaryValue("ReagentRobot_SetGripperOpen"), self.__GetBinaryValue("ReagentRobot_SetGripperClose"), 
                self.__GetBinaryValue("ReagentRobot_SetGasTransferUp"), self.__GetBinaryValue("ReagentRobot_SetGasTransferDown"), 
                self.__GetBinaryValue("ReagentRobot_GripperUp"), self.__GetBinaryValue("ReagentRobot_GripperDown"), 
                self.__GetBinaryValue("ReagentRobot_GripperOpen"), self.__GetBinaryValue("ReagentRobot_GripperClose"), 
                self.__GetBinaryValue("ReagentRobot_GasTransferUp"), self.__GetBinaryValue("ReagentRobot_GasTransferDown"), 
                self.__GetRobotStatus(self.__nReagentXAxis), self.__GetRobotError(self.__nReagentXAxis), 
                self.__GetRobotControlWord(self.__nReagentXAxis), self.__GetRobotCheckWord(self.__nReagentXAxis), 
                self.__GetRobotStatus(self.__nReagentYAxis), self.__GetRobotError(self.__nReagentYAxis), 
                self.__GetRobotControlWord(self.__nReagentYAxis), self.__GetRobotCheckWord(self.__nReagentYAxis))
            pModel["Reactor1"]["Motion"].updateState(nReactor1RobotSetPosition, nReactor1RobotActualPosition, nReactor1RobotSetPositionRaw, nReactor1RobotActualPositionRaw,
                self.__GetBinaryValue("Reactor1_SetReactorUp"), self.__GetBinaryValue("Reactor1_SetReactorDown"), self.__GetBinaryValue("Reactor1_ReactorUp"),
                self.__GetBinaryValue("Reactor1_ReactorDown"), self.__GetRobotStatus(self.__LookUpReactorAxis(1)), self.__GetRobotError(self.__LookUpReactorAxis(1)),
                self.__GetRobotControlWord(self.__LookUpReactorAxis(1)), self.__GetRobotCheckWord(self.__LookUpReactorAxis(1)))
            pModel["Reactor1"]["Stopcock1"].updateState(self.__GetBinaryValue("Reactor1_Stopcock1ValveCW"), self.__GetBinaryValue("Reactor1_Stopcock1ValveCCW"))
            pModel["Reactor1"]["Stopcock2"].updateState(self.__GetBinaryValue("Reactor1_Stopcock2ValveCW"), self.__GetBinaryValue("Reactor1_Stopcock2ValveCCW"))
            pModel["Reactor1"]["Stopcock3"].updateState(self.__GetBinaryValue("Reactor1_Stopcock3ValveCW"), self.__GetBinaryValue("Reactor1_Stopcock3ValveCCW"))
            pModel["Reactor1"]["Stir"].updateState(self.__GetAnalogValue("Reactor1_StirMotor"))
            pModel["Reactor1"]["Thermocouple"].updateState(self.__GetHeaterOn(1, 1), self.__GetHeaterOn(1, 2), self.__GetHeaterOn(1, 3),
                self.__GetThermocontrollerSetValue("Reactor1_TemperatureController1"), self.__GetThermocontrollerSetValue("Reactor1_TemperatureController2"),
                self.__GetThermocontrollerSetValue("Reactor1_TemperatureController3"), self.__GetThermocontrollerActualValue("Reactor1_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor1_TemperatureController2"), self.__GetThermocontrollerActualValue("Reactor1_TemperatureController3"))
            pModel["Reactor1"]["Radiation"].updateState(self.__GetRadiation(1))
            pModel["Reactor2"]["Motion"].updateState(nReactor2RobotSetPosition, nReactor2RobotActualPosition, nReactor2RobotSetPositionRaw, nReactor2RobotActualPositionRaw,
                self.__GetBinaryValue("Reactor2_SetReactorUp"), self.__GetBinaryValue("Reactor2_SetReactorDown"), self.__GetBinaryValue("Reactor2_ReactorUp"),
                self.__GetBinaryValue("Reactor2_ReactorDown"), self.__GetRobotStatus(self.__LookUpReactorAxis(2)), self.__GetRobotError(self.__LookUpReactorAxis(2)),
                self.__GetRobotControlWord(self.__LookUpReactorAxis(2)), self.__GetRobotCheckWord(self.__LookUpReactorAxis(2)))
            pModel["Reactor2"]["Stopcock1"].updateState(self.__GetBinaryValue("Reactor2_Stopcock1ValveCW"), self.__GetBinaryValue("Reactor2_Stopcock1ValveCCW"))
            pModel["Reactor2"]["Stopcock2"].updateState(self.__GetBinaryValue("Reactor2_Stopcock2ValveCW"), self.__GetBinaryValue("Reactor2_Stopcock2ValveCCW"))
            pModel["Reactor2"]["Stopcock3"].updateState(self.__GetBinaryValue("Reactor2_Stopcock3ValveCW"), self.__GetBinaryValue("Reactor2_Stopcock3ValveCCW"))
            pModel["Reactor2"]["Stir"].updateState(self.__GetAnalogValue("Reactor2_StirMotor"))
            pModel["Reactor2"]["Thermocouple"].updateState(self.__GetHeaterOn(2, 1), self.__GetHeaterOn(2, 2), self.__GetHeaterOn(2, 3),
                self.__GetThermocontrollerSetValue("Reactor2_TemperatureController1"), self.__GetThermocontrollerSetValue("Reactor2_TemperatureController2"),
                self.__GetThermocontrollerSetValue("Reactor2_TemperatureController3"), self.__GetThermocontrollerActualValue("Reactor2_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor2_TemperatureController2"), self.__GetThermocontrollerActualValue("Reactor2_TemperatureController3"))
            pModel["Reactor2"]["Radiation"].updateState(self.__GetRadiation(2))
            pModel["Reactor3"]["Motion"].updateState(nReactor3RobotSetPosition, nReactor3RobotActualPosition, nReactor3RobotSetPositionRaw, nReactor3RobotActualPositionRaw,
                self.__GetBinaryValue("Reactor3_SetReactorUp"), self.__GetBinaryValue("Reactor3_SetReactorDown"), self.__GetBinaryValue("Reactor3_ReactorUp"),
                self.__GetBinaryValue("Reactor3_ReactorDown"), self.__GetRobotStatus(self.__LookUpReactorAxis(3)), self.__GetRobotError(self.__LookUpReactorAxis(3)),
                self.__GetRobotControlWord(self.__LookUpReactorAxis(3)), self.__GetRobotCheckWord(self.__LookUpReactorAxis(3)))
            pModel["Reactor3"]["Stopcock1"].updateState(self.__GetBinaryValue("Reactor3_Stopcock1ValveCW"), self.__GetBinaryValue("Reactor3_Stopcock1ValveCCW"))
            pModel["Reactor3"]["Stopcock2"].updateState(self.__GetBinaryValue("Reactor3_Stopcock2ValveCW"), self.__GetBinaryValue("Reactor3_Stopcock2ValveCCW"))
            pModel["Reactor3"]["Stopcock3"].updateState(self.__GetBinaryValue("Reactor3_Stopcock3ValveCW"), self.__GetBinaryValue("Reactor3_Stopcock3ValveCCW"))
            pModel["Reactor3"]["Stir"].updateState(self.__GetAnalogValue("Reactor3_StirMotor"))
            pModel["Reactor3"]["Thermocouple"].updateState(self.__GetHeaterOn(3, 1), self.__GetHeaterOn(3, 2), self.__GetHeaterOn(3, 3),
                self.__GetThermocontrollerSetValue("Reactor3_TemperatureController1"), self.__GetThermocontrollerSetValue("Reactor3_TemperatureController2"),
                self.__GetThermocontrollerSetValue("Reactor3_TemperatureController3"), self.__GetThermocontrollerActualValue("Reactor3_TemperatureController1"),
                self.__GetThermocontrollerActualValue("Reactor3_TemperatureController2"), self.__GetThermocontrollerActualValue("Reactor3_TemperatureController3"))
            pModel["Reactor3"]["Radiation"].updateState(self.__GetRadiation(3))

            # Log the collet temperatures
            if self.__bTempLogging:
                self.__LogTemperatures()
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
        nBit = (nWord >> int(nBitOffset)) & 1
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
        fWord = float(int(sWord, 0x10))
        if self.__GetThermocontrollerDecimalPoint(sHardwareName):
            fWord /= 10
        return fWord
    def __GetThermocontrollerActualValue(self, sHardwareName):
        # Look up the temperature actual offset and return the value
        nOffset = self.__LookUpThermocontrollerActualOffset(sHardwareName)
        sWord = self.__sState[((nOffset - self.__nMemoryLower) * 4):((nOffset - self.__nMemoryLower + 1) * 4)]
        fWord = float(int(sWord, 0x10))
        if self.__GetThermocontrollerDecimalPoint(sHardwareName):
            fWord /= 10
        return fWord
    def __GetThermocontrollerDecimalPoint(self, sHardwareName):
        # Check if this thermocontroller is in our dictionary
        if self.__pThermocontrollerDecimalPointFlags.has_key(sHardwareName):
            return self.__pThermocontrollerDecimalPointFlags[sHardwareName]

        # Look up the decimal point flag
        nWordOffset, nBitOffset = self.__LookUpThermocontrollerDecimalOffset(sHardwareName)
        sWord = self.__sState[((nWordOffset - self.__nMemoryLower) * 4):((nWordOffset - self.__nMemoryLower + 1) * 4)]
        nWord = int(sWord, 0x10)
        bDecimalPointFlag = bool((nWord >> int(nBitOffset)) & 0x1)

        # Remember and return the flag
        self.__pThermocontrollerDecimalPointFlags[sHardwareName] = bDecimalPointFlag
        return bDecimalPointFlag

    # Get vacuum pressure
    def __GetVacuumPressure(self):
        nVacuumPLC = float(self.__GetAnalogValue("VacuumPressure"))
        return ((nVacuumPLC * self.__nVacuumGaugeSlope) + self.__nVacuumGaugeIntercept)

    # Get liquid sensor values
    def __GetLiquidSensor(self, nLiquidSensor):
        return (self.__GetLiquidSensorRaw(nLiquidSensor) < LIQUID_SENSOR_THRESHOLD)
    def __GetLiquidSensorRaw(self, nLiquidSensor):
        return float(self.__GetAnalogValue("LiquidSensor" + str(nLiquidSensor) + "_LiquidValue"))

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
    def __GetReagentRobotSetY(self):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__nReagentYAxis * 4)))
    def __GetReagentRobotActualX(self):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentXAxis * 4)))
    def __GetReagentRobotActualY(self):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__nReagentYAxis * 4)))

    # Get reactor robot positions
    def __GetReactorRobotSetPosition(self, nReactor):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSSET + (self.__LookUpReactorAxis(nReactor) * 4)))
    def __GetReactorRobotActualPosition(self, nReactor):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_AXISPOSREAD + (self.__LookUpReactorAxis(nReactor) * 4)))

    # Get the robot status, error code and check and control words (see ACON_PCON_SPEC.PDF, page 89)
    def __GetRobotStatus(self, nAxis):
        # Get the check word and extract the flags of interest
        nCheckWord = int(self.__GetIntegerValueRaw(ROBONET_CHECK + (nAxis * 4)))
        bHomeComplete = (nCheckWord >> ROBONET_STATUS_HOMECOMPLETE) & 1
        bMoving = (nCheckWord >> ROBONET_STATUS_MOVING) & 1
        bAlarm = (nCheckWord >> ROBONET_STATUS_ALARM) & 1
        bReady = (nCheckWord >> ROBONET_STATUS_READY) & 1

        # Interpret the flags
        if bAlarm:
            return "Error"
        if bReady:
            if bMoving:
                if bHomeComplete:
                    return "Moving"
                else:
                    return "Homing"
            else:
                return "Enabled"
        else:
            if bHomeComplete:
                return "Disabled"
            else:
                return "Init"
    def __GetRobotError(self, nAxis):
        # See if the alarm bit is set in the check word
        nCheckWord = int(self.__GetIntegerValueRaw(ROBONET_CHECK + (nAxis * 4)))
        if ((nCheckWord >> ROBONET_STATUS_ALARM) & 1):
            # Yes, so get the error code
            return (int(self.__GetIntegerValueRaw(ROBONET_ERROR + (nAxis * 4))) & 0x3FF)
        else:
            # No, so there is no error code
            return 0
    def __GetRobotControlWord(self, nAxis):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_CONTROL + (nAxis * 4)))
    def __GetRobotCheckWord(self, nAxis):
        return self.__UnsignedToSigned(self.__GetIntegerValueRaw(ROBONET_CHECK + (nAxis * 4)))

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
    def __LookUpReactorCassetteYOffset(self, nReactor):
        if (nReactor == 1):
            return self.__nReactor1CassetteYOffset
        elif (nReactor == 2):
            return self.__nReactor2CassetteYOffset
        elif (nReactor == 3):
            return self.__nReactor3CassetteYOffset
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
                    "y":str(pDescriptorComponents[0])}
            elif len(pDescriptorComponents) == 2:
                return {"name":sPositionName,
                    "x":str(pDescriptorComponents[0]),
                    "y":str(pDescriptorComponents[1])}
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

    # Look up the temperature decimal offsets
    def __LookUpThermocontrollerDecimalOffset(self, sHardwareName):
        # Look up the hardware component by name
        pHardware = self.__LookUpHardwareName(sHardwareName)

        # Calculate the absolute address of the target word and bit
        nOffset = self.__DetermineHardwareOffset(pHardware)
        if pHardware["loop"] == "1":
            return (nOffset + 0x7), 0x8
        elif pHardware["loop"] == "2":
            return (nOffset + 0x7), 0xc
        elif pHardware["loop"] == "3":
            return (nOffset + 0x11), 0x8
        elif pHardware["loop"] == "4":
           return (nOffset + 0x11), 0xc
        else:
            raise Exception("Invalid thermocontroller loop")

    # Looks up the reagent robot position
    def __LookUpReagentRobotPosition(self, nPositionX, nPositionY):
        # Hit test each reactor
        for nReactor in range(1,4):
            # Hit test each reagent position
            for nReagent in range(1, 12+1):  # Fix for the Transfer reset issue
                pPosition = self.__LookUpRobotPosition("ReagentRobot_Reagent" + str(nReagent))
                nReagentXOffset = self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"])
                nReagentYOffset = self.__LookUpReactorCassetteYOffset(nReactor) + int(pPosition["y"])
                if self.__HitTest(nReagentXOffset, nPositionX) and self.__HitTest(nReagentYOffset, nPositionY):
                    # We're over a reagent
                    return nReactor, nReagent, 0, 0

            # Hit test each reagent delivery position
            for nReagentDelivery in range(1, 3):
                pPosition = self.__LookUpRobotPosition("ReagentRobot_ReagentDelivery" + str(nReagentDelivery))
                nReagentXOffset = self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"])
                nReagentYOffset = self.__LookUpReactorCassetteYOffset(nReactor) + int(pPosition["y"])
                if self.__HitTest(nReagentXOffset, nPositionX) and self.__HitTest(nReagentYOffset, nPositionY):
                    # We're over a reagent delivery position
                    return nReactor, 0, nReagentDelivery, 0
        
            # Hit test the elute position
            pPosition = self.__LookUpRobotPosition("ReagentRobot_Elute")
            nReagentXOffset = self.__LookUpReactorCassetteXOffset(nReactor) + int(pPosition["x"])
            nReagentYOffset = self.__LookUpReactorCassetteYOffset(nReactor) + int(pPosition["y"])
            if self.__HitTest(nReagentXOffset, nPositionX) and self.__HitTest(nReagentYOffset, nPositionY):
                # We're over the elute position
                return nReactor, 0, 0, 1

        # Failed to find match
        return 0, 0, 0, 0
     
    # Look up the reactor robot position
    def __LookUpReactorRobotPosition(self, nReactor, nPositionY):
        # Hit test each reactor position
        nReactorOffset = self.__LookUpReactorOffset(nReactor)
        for sPositionName in self.__pRobotPositions["Reactors"]:
            if self.__HitTest(nPositionY - nReactorOffset, int(self.__pRobotPositions["Reactors"][sPositionName])):
                # We're over a know position
                return sPositionName

        # Check for home
        if nPositionY == 0:
            return "Home"

        # Failed to find a named position
        return "Unknown" 

    # Hit tests the given reagent position
    def __HitTest(self, nPosition, nSetPosition):
        return ((nSetPosition - ROBOT_POSITION_LIMIT) <= nPosition) and ((nSetPosition + ROBOT_POSITION_LIMIT) >= nPosition)

    # Converts from an unsigned integer to a signed integer
    def __UnsignedToSigned(self, nUnsignedInt):
        # Is the MSB set?
        if int(nUnsignedInt) & (1 << 15):
            # Yes, so this is a negative number.  Take the complement of the entire number
            nSignedInt = nUnsignedInt - 0xffff
        else:
            # No, so this is a positive number
            nSignedInt = nUnsignedInt

        # Return the signed integer
        return nSignedInt

    # Checks for runaway temperatures
    def __CheckForRunawayTemp(self, nReactor, nTemperatureController):
        # Skip if we aren't heating
        fSetTemperature = self.__GetThermocontrollerSetValue("Reactor" + str(nReactor) + "_TemperatureController" + str(nTemperatureController))
        if not self.__GetHeaterOn(nReactor, nTemperatureController) or (fSetTemperature == 0):
            return

        # Calculate the temperature of the entire reactor
        fAverageTemp = (self.__GetThermocontrollerActualValue("Reactor" + str(nReactor) + "_TemperatureController1") +
            self.__GetThermocontrollerActualValue("Reactor" + str(nReactor) + "_TemperatureController2") +
            self.__GetThermocontrollerActualValue("Reactor" + str(nReactor) + "_TemperatureController3")) / 3

        # Raise an alarm if this heater is 20 degrees over the average
        if self.__GetThermocontrollerActualValue("Reactor" + str(nReactor) + "_TemperatureController" + str(nTemperatureController)) > (fAverageTemp + 20):
            for nReactor in range(1, 4):
                self.HeaterOff(nReactor)
            raise RunawayHeaterException(nReactor)

    # Begin logging temperatures to a file
    def __StartTempLogging(self):
        if sys.platform == "win32":
            self.__sLogFile = "temp_profile.txt"
        else:
            self.__sLogFile = os.path.join("/home", "sofiebio", "Desktop/temp_profile.txt")
        self.__startTime = time.time()
        pLogFile = open(self.__sLogFile, "w")
        pLogFile.write("Time,")
        pLogFile.write("H1C1Set,H1C2Set,H1C3Set,H1C1Actual,H1C2Actual,H1C3Actual,")
        pLogFile.write("H2C1Set,H2C2Set,H2C3Set,H2C1Actual,H2C2Actual,H2C3Actual,")
        pLogFile.write("H3C1Set,H3C2Set,H3C3Set,H3C1Actual,H3C2Actual,H3C3Actual\n")
        pLogFile.flush()
        pLogFile.close()
        self.__bTempLogging = True

    # Creates a temperature log file entry
    def __LogTemperatures(self):
        if not self.__bTempLogging:
            return
        nCurrentTime = time.time()
        pLogFile = open(self.__sLogFile, "a")
        pLogFile.write("%.1f," % (nCurrentTime - self.__startTime))
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor1_TemperatureController1")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor1_TemperatureController2")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor1_TemperatureController3")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor1_TemperatureController1")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor1_TemperatureController2")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor1_TemperatureController3")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor2_TemperatureController1")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor2_TemperatureController2")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor2_TemperatureController3")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor2_TemperatureController1")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor2_TemperatureController2")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor2_TemperatureController3")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor3_TemperatureController1")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor3_TemperatureController2")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerSetValue("Reactor3_TemperatureController3")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor3_TemperatureController1")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor3_TemperatureController2")) + ",")
        pLogFile.write(str(self.__GetThermocontrollerActualValue("Reactor3_TemperatureController3")) + "\n")
        pLogFile.flush()
        pLogFile.close()

    # Stops logging temperatures
    def __StopTempLogging(self):
        self.__bTempLogging = False

