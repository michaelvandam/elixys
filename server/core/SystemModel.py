"""System Model

Elixys System Model
"""

# Imports
from configobj import ConfigObj
import time
import threading
import os.path
import json
import sys
sys.path.append("/opt/elixys/hardware/")
sys.path.append("/opt/elixys/core/unitoperations")
from HardwareComm import HardwareComm
from StateUpdateThread import StateUpdateThread
from TemperatureControlModel import TemperatureControlModel
from MotionModel import MotionModel
from StirMotorModel import StirMotorModel
from RadiationDetectorModel import RadiationDetectorModel
from StopcockValveModel import StopcockValveModel
from ReagentDeliveryModel import ReagentDeliveryModel
from CoolingSystemModel import CoolingSystemModel
from VacuumSystemModel import VacuumSystemModel
from PressureRegulatorModel import PressureRegulatorModel
from LiquidSensorsModel import LiquidSensorsModel
from ValvesModel import ValvesModel
import TimedLock
import UnitOperation
import Utilities
import copy
import socket
import rpyc
from DBComm import *

# Constants
STATECOMMONCOLUMN1WIDTH = 45
STATECOMMONCOLUMN2WIDTH = 12
STATEREACTORCOLUMN1WIDTH = 35
STATEREACTORCOLUMN2WIDTH = 13

class SystemModel:
  def __init__(self, pHardwareComm, pDatabase):
    """SystemModel constructor"""
    # Remember the hardware and database layers
    self.hardwareComm = pHardwareComm
    self.database = pDatabase
    
    # Pass a pointer to the system model so the hardware layer can update our state
    self.hardwareComm.SetSystemModel(self)
    
    # Create the empty system model and a lock to protect it
    self.model = {}
    self.modelLock = TimedLock.TimedLock()

    # Load the system model from the INI file
    sSystemModel = "/opt/elixys/core/SystemModel.ini"
    if not os.path.exists(sSystemModel):
        print "Invalid path to INI files"
        return
    self.SystemComponents = ConfigObj(sSystemModel)
    
    # Build the system model
    for key,value in self.SystemComponents.items():
      if key == "CoolingSystem":
        if value == "True":
          self.model[key] = CoolingSystemModel(key, self.hardwareComm, self.modelLock)
      elif key == "VacuumSystem":
        if value == "True":
          self.model[key] = VacuumSystemModel(key, self.hardwareComm, self.modelLock)
      elif key == "Valves":
        if value == "True":
          self.model[key] = ValvesModel(key, self.hardwareComm, self.modelLock)
      elif key == "PressureRegulators":
        for nPressureRegulator in range(1, int(value) + 1):
          sPressureRegulator = "PressureRegulator" + str(nPressureRegulator)
          self.model[sPressureRegulator] = PressureRegulatorModel(sPressureRegulator, nPressureRegulator, self.hardwareComm, self.modelLock)
      elif key == "LiquidSensors":
        if value == "True":
          self.model[key] = LiquidSensorsModel(key, self.hardwareComm, self.modelLock)
      elif key == "ReagentDelivery":
        if value == "True":
          self.model[key] = ReagentDeliveryModel(key, self.hardwareComm, self.modelLock)
      elif key[:7] == 'Reactor':
          sReactor = key
          nReactor = int(key[7:])
          nStopcocks = int(value["Stopcocks"])
          self.model[sReactor] = {}
          self.model[sReactor]["Motion"] = MotionModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
          for nStopcock in range(1, nStopcocks + 1):
            self.model[sReactor]["Stopcock" + str(nStopcock)] = StopcockValveModel(sReactor, nReactor, nStopcock, self.hardwareComm, self.modelLock)
          self.model[sReactor]["Thermocouple"] = TemperatureControlModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
          self.model[sReactor]["Stir"] = StirMotorModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
          self.model[sReactor]["Radiation"] = RadiationDetectorModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
      else:
        raise Exception("Unknown system component: " + key)

    # Initialize variables
    self.stateUpdateThread = None
    self.stateUpdateThreadTerminateEvent = None
    self.__pStateMonitor = None
    self.__bStateMonitorError = False
    self.__pUnitOperation = None
    self.__pStateObject = None
    self.__sStateString = ""
    self.__pStateLock = TimedLock.TimedLock()
    
  def StartUp(self):
    """Starts the system model"""
    if self.stateUpdateThread != None:
      self.ShutDown()
    self.stateUpdateThread = StateUpdateThread()
    self.stateUpdateThreadTerminateEvent = threading.Event()
    self.stateUpdateThread.SetParameters(self.hardwareComm, self.stateUpdateThreadTerminateEvent)
    self.stateUpdateThread.setDaemon(True)
    self.stateUpdateThread.start()
        
  def ShutDown(self):
    """Shuts down the system model"""
    if self.stateUpdateThread != None:
      self.stateUpdateThreadTerminateEvent.set()
      self.stateUpdateThread.join()
      self.stateUpdateThread = None
      self.stateUpdateThreadTerminateEvent = None

  def CheckForError(self):
    """Checks if the state update thread has encountered an error"""
    if self.stateUpdateThread != None:
      if self.stateUpdateThread.GetError() != "":
        raise Exception(self.stateUpdateThread.GetError())
      if not self.stateUpdateThread.is_alive():
        raise Exception("State update thread died expectedly")

  def SetUnitOperation(self, pUnitOperation):
    """Sets the current unit operation"""
    self.__pUnitOperation = pUnitOperation

  def GetUnitOperation(self):
    """Returns the current unit operation"""
    if (self.__pUnitOperation != None) and self.__pUnitOperation.is_alive():
        return self.__pUnitOperation
    else:
        return None
    
  def LockSystemModel(self):
    """Acquire the mutex lock and return the system model"""
    self.modelLock.Acquire()
    return self.model
    
  def UnlockSystemModel(self):
    """Release the system model lock"""
    self.modelLock.Release()

  def ModelUpdated(self):
    """Called when the system model has been updated"""
    # Are we a fake PLC?
    if not self.hardwareComm.IsFakePLC():
      # No, so update the system
      self.__UpdateState()

      # Attempt to connect to the state monitor
      if self.__pStateMonitor == None:
        try:
          self.__pStateMonitor = rpyc.connect("localhost", 18861)
          self.database.SystemLog(LOG_INFO, "System", "Connection to state monitor established")
          self.__bStateMonitorError = False
        except socket.error, ex:
          if not self.__bStateMonitorError:
            self.database.SystemLog(LOG_INFO, "System", "Failed to connect to state monitor")
          self.__pStateMonitor = None
          self.__bStateMonitorError = True

      # Update the state monitor
      if self.__pStateMonitor != None:
        try:
          self.__pStateMonitor.root.UpdateState(self.GetStateString())
        except EOFError, ex:
          # Catch EOFErrors in the event that the state monitor process dies
          self.database.SystemLog(LOG_INFO, "System", "Failed to update state monitor")
          self.__pStateMonitor = None
          self.__bStateMonitorError = True

  def GetStateObject(self):
    """Returns the state as an object"""
    self.__pStateLock.Acquire()
    try:
      pStateObject = copy.deepcopy(self.__pStateObject)
    finally:
      self.__pStateLock.Release()
    return pStateObject

  def GetStateString(self):
    """Returns the state to a string"""
    self.__pStateLock.Acquire()
    try:
      pStateString = copy.copy(self.__sStateString)
    finally:
      self.__pStateLock.Release()
    return pStateString

  def __UpdateState(self):
    # Acquire a lock on the system model and our state variables
    self.LockSystemModel()
    self.__pStateLock.Acquire()

    # Dump the state in a try/except/finally block to make sure we release our locks
    try:
      # Initialize variables
      self.__pStateObject = {"type":"serverstate"}
      self.__sStateString = ""

      # Create hardware state and string header
      self.__pStateObject["hardwarestate"] = {"type":"hardwarestate"}
      self.__sStateString += self.__PadString("Component", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("Set", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("Actual", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("----------------------------------", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("--------", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("--------", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Vacuum system
      bVacuumSystemOn = self.model["VacuumSystem"].getVacuumSystemOn(False)
      fVacuumSystemPressure = self.model["VacuumSystem"].getVacuumSystemPressure(False)
      self.__pStateObject["hardwarestate"]["vacuum"] = {"type":"vacuumstate"}
      self.__pStateObject["hardwarestate"]["vacuum"]["on"] = bVacuumSystemOn
      self.__pStateObject["hardwarestate"]["vacuum"]["vacuum"] = fVacuumSystemPressure
      self.__sStateString += self.__PadString("Vacuum system (on/pressure)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bVacuumSystemOn) + "/%.1f"%(fVacuumSystemPressure), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Cooling system
      bCoolingSystemOn = self.model["CoolingSystem"].getCoolingSystemOn(False)
      self.__pStateObject["hardwarestate"]["cooling"] = bCoolingSystemOn
      self.__sStateString += self.__PadString("Cooling system on", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bCoolingSystemOn), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Pressure regulators
      fPressureRegulator1SetPressure = self.model["PressureRegulator1"].getSetPressure(False)
      fPressureRegulator1ActualPressure = self.model["PressureRegulator1"].getCurrentPressure(False)
      fPressureRegulator2SetPressure = self.model["PressureRegulator2"].getSetPressure(False)
      fPressureRegulator2ActualPressure = self.model["PressureRegulator2"].getCurrentPressure(False)
      self.__pStateObject["hardwarestate"]["pressureregulators"] = []
      self.__pStateObject["hardwarestate"]["pressureregulators"].append({"type":"pressureregulatorstate",
        "name":"Pneumatics",
        "pressure":fPressureRegulator1SetPressure})
      self.__pStateObject["hardwarestate"]["pressureregulators"].append({"type":"pressureregulatorstate",
        "name":"Gas",
        "pressure":fPressureRegulator2SetPressure})
      self.__sStateString += self.__PadString("Pressure regulator 1", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("%.1f"%(fPressureRegulator1SetPressure), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("%.1f"%(fPressureRegulator1ActualPressure), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Pressure regulator 2", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("%.1f"%(fPressureRegulator2SetPressure), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("%.1f"%(fPressureRegulator2ActualPressure), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Liquid sensors
      bLiquidSensor1 = self.model["LiquidSensors"].getLiquidSensor1(False)
      bLiquidSensor2 = self.model["LiquidSensors"].getLiquidSensor2(False)
      fLiquidSensorRaw1 = self.model["LiquidSensors"].getLiquidSensorRaw1(False)
      fLiquidSensorRaw2 = self.model["LiquidSensors"].getLiquidSensorRaw2(False)
      self.__pStateObject["hardwarestate"]["liquidsensors"] = []
      self.__pStateObject["hardwarestate"]["liquidsensors"].append({"type":"liquidsensorstate",
        "name":"LS1",
        "liquidpresent":bLiquidSensor1})
      self.__pStateObject["hardwarestate"]["liquidsensors"].append({"type":"liquidsensorstate",
        "name":"LS2",
        "liquidpresent":bLiquidSensor2})
      self.__sStateString += self.__PadString("Liquid sensor 1 (present/raw)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bLiquidSensor2) + "/%.1f"%(fLiquidSensorRaw1), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Liquid sensor 2 (present/raw)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bLiquidSensor1) + "/%.1f"%(fLiquidSensorRaw2), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Valves
      bGasTransferValveOpen = self.model["Valves"].getGasTransferValveOpen(False)
      bF18LoadValveOpen = self.model["Valves"].getF18LoadValveOpen(False)
      bHPLCInjectValveOpen = self.model["Valves"].getHPLCInjectValveOpen(False)
      self.__pStateObject["hardwarestate"]["valves"] = {"type":"valvesstate"}
      self.__pStateObject["hardwarestate"]["valves"]["gastransfervalve"] = bGasTransferValveOpen
      self.__pStateObject["hardwarestate"]["valves"]["f18loadvalve"] = bF18LoadValveOpen
      self.__pStateObject["hardwarestate"]["valves"]["hplcinjectvalve"] = bHPLCInjectValveOpen
      self.__sStateString += self.__PadString("Gas transfer valve open", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bGasTransferValveOpen), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("F-18 load valve open", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bF18LoadValveOpen), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("HPLC inject valve open", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bHPLCInjectValveOpen), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reagent robot position
      nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery, \
        nReagentRobotSetPositionElute = self.model["ReagentDelivery"].getSetPosition(False)
      nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawY = self.model["ReagentDelivery"].getSetPositionRaw(False)
      sReagentRobotSetPositionName1, sReagentRobotSetPositionName2 = self.model["ReagentDelivery"].getSetPositionName(False)
      nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery, \
        nReagentRobotCurrentPositionElute = self.model["ReagentDelivery"].getCurrentPosition(False)
      nReagentRobotCurrentPositionRawX, nReagentRobotCurrentPositionRawY = self.model["ReagentDelivery"].getCurrentPositionRaw(False)
      sReagentRobotCurrentPositionName1, sReagentRobotCurrentPositionName2 = self.model["ReagentDelivery"].getCurrentPositionName(False)
      sReagentRobotCurrentStatusX, sReagentRobotCurrentStatusY = self.model["ReagentDelivery"].getRobotStatus(False)
      nReagentRobotCurrentErrorX, nReagentRobotCurrentErrorY = self.model["ReagentDelivery"].getRobotError(False)
      nReagentRobotXControlWord, nReagentRobotXCheckWord = self.model["ReagentDelivery"].getRobotXControlWords(False)
      nReagentRobotYControlWord, nReagentRobotYCheckWord = self.model["ReagentDelivery"].getRobotYControlWords(False)
      self.__pStateObject["hardwarestate"]["reagentrobot"] = {"type":"reagentrobotstate"}
      self.__pStateObject["hardwarestate"]["reagentrobot"]["position"] = {"type":"reagentrobotposition",
        "name1":sReagentRobotCurrentPositionName1,
        "name2":sReagentRobotCurrentPositionName2}
      self.__sStateString += "Reagent robot\n"
      self.__sStateString += self.__PadString("  Position", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(sReagentRobotSetPositionName1, STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReagentRobotCurrentPositionName1, STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(sReagentRobotSetPositionName2, STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReagentRobotCurrentPositionName2, STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("  Raw position (x/y)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(nReagentRobotSetPositionRawX) + "/" + str(nReagentRobotSetPositionRawY), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReagentRobotCurrentPositionRawX) + "/" + str(nReagentRobotCurrentPositionRawY), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("  Robot status (x/y)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReagentRobotCurrentStatusX + "/" + sReagentRobotCurrentStatusY, STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("  Robot error (x/y)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReagentRobotCurrentErrorX) + "/" + str(nReagentRobotCurrentErrorY), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("  Robot control (x/y)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReagentRobotXControlWord) + "/" + str(nReagentRobotYControlWord), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("  Robot check (x/y)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReagentRobotXCheckWord) + "/" + str(nReagentRobotYCheckWord), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reagent robot actuators
      bGripperActuatorSetUp = self.model["ReagentDelivery"].getSetGripperUp(False)
      bGripperActuatorSetDown = self.model["ReagentDelivery"].getSetGripperDown(False)
      bGripperActuatorCurrentUp = self.model["ReagentDelivery"].getCurrentGripperUp(False)
      bGripperActuatorCurrentDown = self.model["ReagentDelivery"].getCurrentGripperDown(False)
      bGripperSetOpen = self.model["ReagentDelivery"].getSetGripperOpen(False)
      bGripperSetClose = self.model["ReagentDelivery"].getSetGripperClose(False)
      bGripperCurrentOpen = self.model["ReagentDelivery"].getCurrentGripperOpen(False)
      bGripperCurrentClose = self.model["ReagentDelivery"].getCurrentGripperClose(False)
      bGasTransferActuatorSetUp = self.model["ReagentDelivery"].getSetGasTransferUp(False)
      bGasTransferActuatorSetDown = self.model["ReagentDelivery"].getSetGasTransferDown(False)
      bGasTransferActuatorCurrentUp = self.model["ReagentDelivery"].getCurrentGasTransferUp(False)
      bGasTransferActuatorCurrentDown = self.model["ReagentDelivery"].getCurrentGasTransferDown(False)
      if bGripperActuatorCurrentUp and not bGripperActuatorCurrentDown:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gripperactuator"] = "Up"
      elif not bGripperActuatorCurrentUp and bGripperActuatorCurrentDown:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gripperactuator"] = "Down"
      else:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gripperactuator"] = "Indeterminate"
      if bGripperCurrentOpen and not bGripperCurrentClose:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gripper"] = "Open"
      elif not bGripperCurrentOpen and bGripperCurrentClose:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gripper"] = "Close"
      else:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gripper"] = "Indeterminate"
      if bGasTransferActuatorCurrentUp and not bGasTransferActuatorCurrentDown:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gastransferactuator"] = "Up"
      elif not bGasTransferActuatorCurrentUp and bGasTransferActuatorCurrentDown:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gastransferactuator"] = "Down"
      else:
        self.__pStateObject["hardwarestate"]["reagentrobot"]["gastransferactuator"] = "Indeterminate"
      self.__sStateString += self.__PadString("  Gripper (up/down)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bGripperActuatorSetUp) + "/" + self.__BoolToString(bGripperActuatorSetDown), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bGripperActuatorCurrentUp) + "/" + self.__BoolToString(bGripperActuatorCurrentDown), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("  Gripper (open/close)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bGripperSetOpen) + "/" + self.__BoolToString(bGripperSetClose), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bGripperCurrentOpen) + "/" + self.__BoolToString(bGripperCurrentClose), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("  Gas transfer (up/down)", STATECOMMONCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bGasTransferActuatorSetUp) + "/" + self.__BoolToString(bGasTransferActuatorSetDown), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bGasTransferActuatorCurrentUp) + "/" + self.__BoolToString(bGasTransferActuatorCurrentDown), STATECOMMONCOLUMN2WIDTH)
      self.__sStateString += "\n\n"

      # Initialize reactors
      self.__pStateObject["hardwarestate"]["reactors"] = []
      self.__pStateObject["hardwarestate"]["reactors"].append({"type":"reactorstate"})
      self.__pStateObject["hardwarestate"]["reactors"][0]["number"] = 1
      self.__pStateObject["hardwarestate"]["reactors"].append({"type":"reactorstate"})
      self.__pStateObject["hardwarestate"]["reactors"][1]["number"] = 2
      self.__pStateObject["hardwarestate"]["reactors"].append({"type":"reactorstate"})
      self.__pStateObject["hardwarestate"]["reactors"][2]["number"] = 3
      self.__sStateString += self.__PadString("Reactor", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("1", STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("2", STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("3", STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("----------------------------", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString("------", STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("------", STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString("------", STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor positions
      sReactor1SetPosition = self.model["Reactor1"]["Motion"].getSetPosition(False)
      sReactor2SetPosition = self.model["Reactor2"]["Motion"].getSetPosition(False)
      sReactor3SetPosition = self.model["Reactor3"]["Motion"].getSetPosition(False)
      sReactor1CurrentPosition = self.model["Reactor1"]["Motion"].getCurrentPosition(False)
      sReactor2CurrentPosition = self.model["Reactor2"]["Motion"].getCurrentPosition(False)
      sReactor3CurrentPosition = self.model["Reactor3"]["Motion"].getCurrentPosition(False)
      nReactor1SetPositionRaw = self.model["Reactor1"]["Motion"].getSetPositionRaw(False)
      nReactor2SetPositionRaw = self.model["Reactor2"]["Motion"].getSetPositionRaw(False)
      nReactor3SetPositionRaw = self.model["Reactor3"]["Motion"].getSetPositionRaw(False)
      nReactor1CurrentPositionRaw = self.model["Reactor1"]["Motion"].getCurrentPositionRaw(False)
      nReactor2CurrentPositionRaw = self.model["Reactor2"]["Motion"].getCurrentPositionRaw(False)
      nReactor3CurrentPositionRaw = self.model["Reactor3"]["Motion"].getCurrentPositionRaw(False)
      self.__sStateString += self.__PadString("Set position", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(sReactor1SetPosition, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReactor2SetPosition, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReactor3SetPosition, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Actual position", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(sReactor1CurrentPosition, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReactor2CurrentPosition, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReactor3CurrentPosition, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Raw position (set/actual)", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(nReactor1SetPositionRaw) + "/" + str(nReactor1CurrentPositionRaw), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor2SetPositionRaw) + "/" + str(nReactor2CurrentPositionRaw), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor3SetPositionRaw) + "/" + str(nReactor3CurrentPositionRaw), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor robot status
      sReactor1RobotStatus = self.model["Reactor1"]["Motion"].getCurrentRobotStatus(False)
      sReactor2RobotStatus = self.model["Reactor2"]["Motion"].getCurrentRobotStatus(False)
      sReactor3RobotStatus = self.model["Reactor3"]["Motion"].getCurrentRobotStatus(False)
      nReactor1RobotError = self.model["Reactor1"]["Motion"].getCurrentRobotError(False)
      nReactor2RobotError = self.model["Reactor2"]["Motion"].getCurrentRobotError(False)
      nReactor3RobotError = self.model["Reactor3"]["Motion"].getCurrentRobotError(False)
      nReactor1RobotControlWord, nReactor1RobotCheckWord = self.model["Reactor1"]["Motion"].getCurrentRobotControlWords(False)
      nReactor2RobotControlWord, nReactor2RobotCheckWord = self.model["Reactor2"]["Motion"].getCurrentRobotControlWords(False)
      nReactor3RobotControlWord, nReactor3RobotCheckWord = self.model["Reactor3"]["Motion"].getCurrentRobotControlWords(False)
      self.__sStateString += self.__PadString("Robot status", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(sReactor1RobotStatus, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReactor2RobotStatus, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(sReactor3RobotStatus, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Robot error", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(nReactor1RobotError), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor2RobotError), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor3RobotError), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Robot control", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(nReactor1RobotControlWord), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor2RobotControlWord), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor3RobotControlWord), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Robot check", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(nReactor1RobotCheckWord), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor2RobotCheckWord), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor3RobotCheckWord), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor vertical position
      bReactor1SetUp = self.model["Reactor1"]["Motion"].getSetReactorUp(False)
      bReactor1SetDown = self.model["Reactor1"]["Motion"].getSetReactorDown(False)
      bReactor1CurrentUp = self.model["Reactor1"]["Motion"].getCurrentReactorUp(False)
      bReactor1CurrentDown = self.model["Reactor1"]["Motion"].getCurrentReactorDown(False)
      sReactor1VerticalPosition = self.__GetReactorPosition(bReactor1CurrentUp, bReactor1CurrentDown)
      bReactor2SetUp = self.model["Reactor2"]["Motion"].getSetReactorUp(False)
      bReactor2SetDown = self.model["Reactor2"]["Motion"].getSetReactorDown(False)
      bReactor2CurrentUp = self.model["Reactor2"]["Motion"].getCurrentReactorUp(False)
      bReactor2CurrentDown = self.model["Reactor2"]["Motion"].getCurrentReactorDown(False)
      sReactor2VerticalPosition = self.__GetReactorPosition(bReactor1CurrentUp, bReactor1CurrentDown)
      bReactor3SetUp = self.model["Reactor3"]["Motion"].getSetReactorUp(False)
      bReactor3SetDown = self.model["Reactor3"]["Motion"].getSetReactorDown(False)
      bReactor3CurrentUp = self.model["Reactor3"]["Motion"].getCurrentReactorUp(False)
      bReactor3CurrentDown = self.model["Reactor3"]["Motion"].getCurrentReactorDown(False)
      sReactor3VerticalPosition = self.__GetReactorPosition(bReactor1CurrentUp, bReactor1CurrentDown)
      self.__pStateObject["hardwarestate"]["reactors"][0]["position"] = {"type":"reactorposition",
        "horizontal":sReactor1CurrentPosition,
        "vertical":sReactor1VerticalPosition}
      self.__pStateObject["hardwarestate"]["reactors"][1]["position"] = {"type":"reactorposition",
        "horizontal":sReactor2CurrentPosition,
        "vertical":sReactor2VerticalPosition}
      self.__pStateObject["hardwarestate"]["reactors"][2]["position"] = {"type":"reactorposition",
        "horizontal":sReactor3CurrentPosition,
        "vertical":sReactor3VerticalPosition}
      self.__sStateString += self.__PadString("Reactor up (set/actual)", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor1SetUp) + "/" + self.__BoolToString(bReactor1CurrentUp), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor2SetUp) + "/" + self.__BoolToString(bReactor2CurrentUp), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor3SetUp) + "/" + self.__BoolToString(bReactor3CurrentUp), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Reactor down (set/actual)", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor1SetDown) + "/" + self.__BoolToString(bReactor1CurrentDown), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor2SetDown) + "/" + self.__BoolToString(bReactor2CurrentDown), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor3SetDown) + "/" + self.__BoolToString(bReactor3CurrentDown), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor stopcocks
      sReactor1Stopcock1 = self.model["Reactor1"]["Stopcock1"].getPosition(False)
      sReactor1Stopcock2 = self.model["Reactor1"]["Stopcock2"].getPosition(False)
      sReactor1Stopcock3 = self.model["Reactor1"]["Stopcock3"].getPosition(False)
      sReactor2Stopcock1 = self.model["Reactor2"]["Stopcock1"].getPosition(False)
      sReactor3Stopcock1 = self.model["Reactor3"]["Stopcock1"].getPosition(False)
      self.__pStateObject["hardwarestate"]["reactors"][0]["transferposition"] = self.__GetTransferPosition(sReactor1Stopcock1)
      self.__pStateObject["hardwarestate"]["reactors"][0]["columnposition"] = self.__GetColumnPosition(sReactor1Stopcock2, sReactor1Stopcock3)
      self.__pStateObject["hardwarestate"]["reactors"][1]["transferposition"] = self.__GetTransferPosition(sReactor2Stopcock1)
      self.__pStateObject["hardwarestate"]["reactors"][2]["transferposition"] = self.__GetTransferPosition(sReactor3Stopcock1)
      self.__sStateString += self.__PadString("Stopcock positions (1/2/3)", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(sReactor1Stopcock1) + "/" + str(sReactor1Stopcock2) + "/" + str(sReactor1Stopcock3), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(sReactor2Stopcock1), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(sReactor3Stopcock1), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor heaters
      bReactor1Collet1On = self.model["Reactor1"]["Thermocouple"].getHeater1On(False)
      fReactor1Collet1SetTemperature = self.model["Reactor1"]["Thermocouple"].getHeater1SetTemperature(False)
      fReactor1Collet1CurrentTemperature = self.model["Reactor1"]["Thermocouple"].getHeater1CurrentTemperature(False)
      bReactor1Collet2On = self.model["Reactor1"]["Thermocouple"].getHeater2On(False)
      fReactor1Collet2SetTemperature = self.model["Reactor1"]["Thermocouple"].getHeater2SetTemperature(False)
      fReactor1Collet2CurrentTemperature = self.model["Reactor1"]["Thermocouple"].getHeater2CurrentTemperature(False)
      bReactor1Collet3On = self.model["Reactor1"]["Thermocouple"].getHeater3On(False)
      fReactor1Collet3SetTemperature = self.model["Reactor1"]["Thermocouple"].getHeater3SetTemperature(False)
      fReactor1Collet3CurrentTemperature = self.model["Reactor1"]["Thermocouple"].getHeater3CurrentTemperature(False)
      bReactor2Collet1On = self.model["Reactor2"]["Thermocouple"].getHeater1On(False)
      fReactor2Collet1SetTemperature = self.model["Reactor2"]["Thermocouple"].getHeater1SetTemperature(False)
      fReactor2Collet1CurrentTemperature = self.model["Reactor2"]["Thermocouple"].getHeater1CurrentTemperature(False)
      bReactor2Collet2On = self.model["Reactor2"]["Thermocouple"].getHeater2On(False)
      fReactor2Collet2SetTemperature = self.model["Reactor2"]["Thermocouple"].getHeater2SetTemperature(False)
      fReactor2Collet2CurrentTemperature = self.model["Reactor2"]["Thermocouple"].getHeater2CurrentTemperature(False)
      bReactor2Collet3On = self.model["Reactor2"]["Thermocouple"].getHeater3On(False)
      fReactor2Collet3SetTemperature = self.model["Reactor2"]["Thermocouple"].getHeater3SetTemperature(False)
      fReactor2Collet3CurrentTemperature = self.model["Reactor2"]["Thermocouple"].getHeater3CurrentTemperature(False)
      bReactor3Collet1On = self.model["Reactor3"]["Thermocouple"].getHeater1On(False)
      fReactor3Collet1SetTemperature = self.model["Reactor3"]["Thermocouple"].getHeater1SetTemperature(False)
      fReactor3Collet1CurrentTemperature = self.model["Reactor3"]["Thermocouple"].getHeater1CurrentTemperature(False)
      bReactor3Collet2On = self.model["Reactor3"]["Thermocouple"].getHeater2On(False)
      fReactor3Collet2SetTemperature = self.model["Reactor3"]["Thermocouple"].getHeater2SetTemperature(False)
      fReactor3Collet2CurrentTemperature = self.model["Reactor3"]["Thermocouple"].getHeater2CurrentTemperature(False)
      bReactor3Collet3On = self.model["Reactor3"]["Thermocouple"].getHeater3On(False)
      fReactor3Collet3SetTemperature = self.model["Reactor3"]["Thermocouple"].getHeater3SetTemperature(False)
      fReactor3Collet3CurrentTemperature = self.model["Reactor3"]["Thermocouple"].getHeater3CurrentTemperature(False)
      self.__pStateObject["hardwarestate"]["reactors"][0]["temperature"] = (fReactor1Collet1CurrentTemperature + fReactor1Collet2CurrentTemperature + fReactor1Collet3CurrentTemperature) / 3
      self.__pStateObject["hardwarestate"]["reactors"][1]["temperature"] = (fReactor2Collet1CurrentTemperature + fReactor2Collet2CurrentTemperature + fReactor2Collet3CurrentTemperature) / 3
      self.__pStateObject["hardwarestate"]["reactors"][2]["temperature"] = (fReactor3Collet1CurrentTemperature + fReactor3Collet2CurrentTemperature + fReactor3Collet3CurrentTemperature) / 3
      self.__sStateString += self.__PadString("Collet 1 Temp (on/set/actual)", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor1Collet1On) + "/%.1f" % fReactor1Collet1SetTemperature + \
        "/%.1f" % fReactor1Collet1CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor2Collet1On) + "/%.1f" % fReactor2Collet1SetTemperature + \
        "/%.1f" % fReactor2Collet1CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor3Collet1On) + "/%.1f" % fReactor3Collet1SetTemperature + \
        "/%.1f" % fReactor3Collet1CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Collet 2 Temp (on/set/actual)", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor1Collet2On) + "/%.1f" % fReactor1Collet2SetTemperature + \
        "/%.1f" % fReactor1Collet2CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor2Collet2On) + "/%.1f" % fReactor2Collet2SetTemperature + \
        "/%.1f" % fReactor2Collet2CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor3Collet2On) + "/%.1f" % fReactor3Collet2SetTemperature + \
        "/%.1f" % fReactor3Collet2CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"
      self.__sStateString += self.__PadString("Collet 3 Temp (on/set/actual)", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor1Collet3On) + "/%.1f" % fReactor1Collet3SetTemperature + \
        "/%.1f" % fReactor1Collet3CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor2Collet3On) + "/%.1f" % fReactor2Collet3SetTemperature + \
        "/%.1f" % fReactor2Collet3CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(self.__BoolToString(bReactor3Collet3On) + "/%.1f" % fReactor3Collet3SetTemperature + \
        "/%.1f" % fReactor3Collet3CurrentTemperature, STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor stir motors
      nReactor1StirMotorSpeed = self.model["Reactor1"]["Stir"].getCurrentSpeed(False)
      nReactor2StirMotorSpeed = self.model["Reactor2"]["Stir"].getCurrentSpeed(False)
      nReactor3StirMotorSpeed = self.model["Reactor3"]["Stir"].getCurrentSpeed(False)
      self.__pStateObject["hardwarestate"]["reactors"][0]["stirspeed"] = nReactor1StirMotorSpeed
      self.__pStateObject["hardwarestate"]["reactors"][1]["stirspeed"] = nReactor2StirMotorSpeed
      self.__pStateObject["hardwarestate"]["reactors"][2]["stirspeed"] = nReactor3StirMotorSpeed
      self.__sStateString += self.__PadString("Stir motor", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(nReactor1StirMotorSpeed), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor2StirMotorSpeed), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(nReactor3StirMotorSpeed), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor radiation detectors
      fReactor1RadiationDetector = self.model["Reactor1"]["Radiation"].getRadiation(False)
      fReactor2RadiationDetector = self.model["Reactor2"]["Radiation"].getRadiation(False)
      fReactor3RadiationDetector = self.model["Reactor3"]["Radiation"].getRadiation(False)
      self.__pStateObject["hardwarestate"]["reactors"][0]["activity"] = fReactor1RadiationDetector
      self.__pStateObject["hardwarestate"]["reactors"][0]["activitytime"] = ""
      self.__pStateObject["hardwarestate"]["reactors"][1]["activity"] = fReactor2RadiationDetector
      self.__pStateObject["hardwarestate"]["reactors"][1]["activitytime"] = ""
      self.__pStateObject["hardwarestate"]["reactors"][2]["activity"] = fReactor3RadiationDetector
      self.__pStateObject["hardwarestate"]["reactors"][2]["activitytime"] = ""
      self.__sStateString += self.__PadString("Radiation detector", STATEREACTORCOLUMN1WIDTH)
      self.__sStateString += self.__PadString(str(fReactor1RadiationDetector), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(fReactor1RadiationDetector), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += self.__PadString(str(fReactor1RadiationDetector), STATEREACTORCOLUMN2WIDTH)
      self.__sStateString += "\n"

      # Reactor video
      if not os.path.isfile("/opt/elixys/demomode"):
        self.__pStateObject["hardwarestate"]["reactors"][0]["video"] = "Reactor1"
        self.__pStateObject["hardwarestate"]["reactors"][1]["video"] = "Reactor2"
        self.__pStateObject["hardwarestate"]["reactors"][2]["video"] = "Reactor3"
      else:
        self.__pStateObject["hardwarestate"]["reactors"][0]["video"] = "mp4:elixys.mp4"
        self.__pStateObject["hardwarestate"]["reactors"][1]["video"] = "mp4:elixys.mp4"
        self.__pStateObject["hardwarestate"]["reactors"][2]["video"] = "mp4:elixys.mp4"

      # Unit operation
      if (self.__pUnitOperation != None) and self.__pUnitOperation.is_alive():
        self.__sStateString += "\n"
        self.__sStateString += "\"" + self.__pUnitOperation.__class__.__name__ + "\" unit operation:\n"
        self.__sStateString += "  " + self.__pUnitOperation.description + "\n"
        self.__sStateString += "  Status: " + self.__pUnitOperation.status + "\n"
        sTimerStatus = self.__pUnitOperation.getTimerStatus()
        if sTimerStatus == "Running":
          self.__sStateString += "  Timer running, time remaining: " + self.__FormatTime(self.__pUnitOperation.getTime()) + "\n"
        elif (sTimerStatus == "Overridden"):
          self.__sStateString += "  Timer paused, time elapsed: " + self.__FormatTime(self.__pUnitOperation.getTime()) + "\n"
        elif self.__pUnitOperation.waitingForUserInput:
          self.__sStateString += "  Waiting for user input\n"

      # Update the database
      if self.database != None:
        self.database.StatusLog(bVacuumSystemOn, fVacuumSystemPressure, bCoolingSystemOn, fPressureRegulator1SetPressure, fPressureRegulator1ActualPressure,
          fPressureRegulator2SetPressure, fPressureRegulator2ActualPressure, bGasTransferValveOpen, bF18LoadValveOpen, bHPLCInjectValveOpen,
          sReagentRobotSetPositionName1 + " " + sReagentRobotSetPositionName2, sReagentRobotCurrentPositionName1 + " " + sReagentRobotCurrentPositionName2,
          nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawY, nReagentRobotCurrentPositionRawX, nReagentRobotCurrentPositionRawY,
          sReagentRobotCurrentStatusX, sReagentRobotCurrentStatusY, nReagentRobotCurrentErrorX, nReagentRobotCurrentErrorY, nReagentRobotXControlWord,
          nReagentRobotYControlWord, nReagentRobotXCheckWord, nReagentRobotYCheckWord, bGripperActuatorSetUp, bGripperActuatorSetDown, bGripperSetOpen,
          bGripperSetClose, bGasTransferActuatorSetUp, bGasTransferActuatorSetDown, bGripperActuatorCurrentUp, bGripperActuatorCurrentDown, bGripperCurrentOpen,
          bGripperCurrentClose, bGasTransferActuatorCurrentUp, bGasTransferActuatorCurrentDown, sReactor1SetPosition, sReactor1CurrentPosition, nReactor1SetPositionRaw, 
          nReactor1CurrentPositionRaw, sReactor1RobotStatus, nReactor1RobotError, nReactor1RobotControlWord, nReactor1RobotCheckWord, bReactor1SetUp, bReactor1SetDown, 
          bReactor1CurrentUp, bReactor1CurrentDown, sReactor1Stopcock1, sReactor1Stopcock2, sReactor1Stopcock3, bReactor1Collet1On, fReactor1Collet1SetTemperature,
          fReactor1Collet1CurrentTemperature, bReactor1Collet2On, fReactor1Collet2SetTemperature, fReactor1Collet2CurrentTemperature, bReactor1Collet3On, 
          fReactor1Collet3SetTemperature, fReactor1Collet3CurrentTemperature, nReactor1StirMotorSpeed, fReactor1RadiationDetector, sReactor2SetPosition, 
          sReactor2CurrentPosition, nReactor2SetPositionRaw, nReactor2CurrentPositionRaw, sReactor2RobotStatus, nReactor2RobotError, nReactor2RobotControlWord,
          nReactor2RobotCheckWord, bReactor2SetUp, bReactor2SetDown, bReactor2CurrentUp, bReactor2CurrentDown, sReactor2Stopcock1, bReactor2Collet1On, 
          fReactor2Collet1SetTemperature, fReactor2Collet1CurrentTemperature, bReactor2Collet2On, fReactor2Collet2SetTemperature, fReactor2Collet2CurrentTemperature,
          bReactor2Collet3On, fReactor2Collet3SetTemperature, fReactor2Collet3CurrentTemperature, nReactor2StirMotorSpeed, fReactor2RadiationDetector, sReactor3SetPosition, 
          sReactor3CurrentPosition, nReactor3SetPositionRaw, nReactor3CurrentPositionRaw, sReactor3RobotStatus, nReactor3RobotError, nReactor3RobotControlWord,
          nReactor3RobotCheckWord, bReactor3SetUp, bReactor3SetDown, bReactor3CurrentUp, bReactor3CurrentDown, sReactor3Stopcock1, bReactor3Collet1On, 
          fReactor3Collet1SetTemperature, fReactor3Collet1CurrentTemperature, bReactor3Collet2On, fReactor3Collet2SetTemperature, fReactor3Collet2CurrentTemperature,
          bReactor3Collet3On, fReactor3Collet3SetTemperature, fReactor3Collet3CurrentTemperature, nReactor3StirMotorSpeed, fReactor3RadiationDetector)
    finally:
        # Release the locks
        self.UnlockSystemModel()
        self.__pStateLock.Release()

  def __FormatTime(self, nTime):
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

  def __PadString(self, sString, nTotalCharacters):
    """Pads a string with whitespace"""
    # Check input string length
    if len(sString) > nTotalCharacters:
      return sString
    
    # Create return string
    sReturn = sString
    for nCount in range(len(sString), nTotalCharacters + 1):
      sReturn += " "
    return sReturn
  
  def __BoolToString(self, bValue):
    """Converts a boolean value to a single character"""
    if bValue:
      return "T"
    else:
      return "F"

  def __GetReactorPosition(self, bReactorUp, bReactorDown):
    """Interprets the boolean values to a string"""
    if bReactorUp and not bReactorDown:
      return "Up"
    elif not bReactorUp and bReactorDown:
      return "Down"
    else:
      return "Indeterminate"

  def __GetTransferPosition(self, sStopcockPosition):
    """Interprets the stopcock position to a string"""
    if sStopcockPosition == UnitOperation.TRANSFERTRAP[0]:
      return "Waste"
    elif sStopcockPosition == UnitOperation.TRANSFERELUTE[0]:
      return "Out"
    else:
      return "Indeterminate"

  def __GetColumnPosition(self, sStopcockPosition1, sStopcockPosition2):
    """Interprets the stopcock positions values to a string"""
    if (sStopcockPosition1 == UnitOperation.F18TRAP[1]) and (sStopcockPosition1 == UnitOperation.F18TRAP[2]):
      return "Load"
    elif (sStopcockPosition1 == UnitOperation.F18ELUTE[1]) and (sStopcockPosition1 == UnitOperation.F18ELUTE[2]):
      return "Elute"
    else:
      return "Indeterminate"

