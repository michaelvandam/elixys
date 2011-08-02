"""System Model

Elixys System Model
"""

# Imports
import time
import threading
import sys
sys.path.append("../hardware/")
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
from ValveModel import ValveModel
from ExternalSystemsModel import ExternalSystemsModel

# Constants
STATECOMMONCOLUMN1WIDTH = 45
STATECOMMONCOLUMN2WIDTH = 12
STATEREACTORCOLUMN1WIDTH = 35
STATEREACTORCOLUMN2WIDTH = 13

class SystemModel:
  def __init__(self, hardwareComm):
    """SystemModel constructor"""
    # Remember the hardware layer
    self.hardwareComm = hardwareComm
    
    # Pass a pointer to the system model so the hardware layer can update our state
    self.hardwareComm.SetSystemModel(self)
    
    # Create the empty system model and a lock to protect it
    self.model = {}
    self.modelLock = threading.Lock()

    # Load the system component from the INI file
    self.SystemComponents = {
      "CoolingSystem":True,
      "VacuumSystem":True,
      "ExternalSystems":True,
      "PressureRegulators":2,
      "ReagentDelivery":True,
      "Reactors":[
        {"Reactor":1, "Stopcocks":3},
        {"Reactor":2, "Stopcocks":1},
        {"Reactor":3, "Stopcocks":1}]}
      
    # Build the system model
    for key,value in self.SystemComponents.items():
      if key == "CoolingSystem":
        if value == True:
          self.model[key] = CoolingSystemModel(key, self.hardwareComm, self.modelLock)
      elif key == "VacuumSystem":
        if value == True:
          self.model[key] = VacuumSystemModel(key, self.hardwareComm, self.modelLock)
      elif key == "ExternalSystems":
        if value == True:
          self.model[key] = ExternalSystemsModel(key, self.hardwareComm, self.modelLock)
      elif key == "PressureRegulators":
        for nPressureRegulator in range(1, value + 1):
          sPressureRegulator = "PressureRegulator" + str(nPressureRegulator)
          self.model[sPressureRegulator] = PressureRegulatorModel(sPressureRegulator, nPressureRegulator, self.hardwareComm, self.modelLock)
      elif key == "ReagentDelivery":
        if value == True:
          self.model[key] = ReagentDeliveryModel(key, self.hardwareComm, self.modelLock)
      elif key == 'Reactors':
        for item in value:
          nReactor = item["Reactor"]
          sReactor = "Reactor" + str(nReactor)
          nStopcocks = item["Stopcocks"]
          self.model[sReactor] = {}
          self.model[sReactor]["Motion"] = MotionModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
          self.model[sReactor]["Valves"] = ValveModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
          for nStopcock in range(1, nStopcocks + 1):
            self.model[sReactor]["Stopcock" + str(nStopcock)] = StopcockValveModel(sReactor, nReactor, nStopcock, self.hardwareComm, self.modelLock)
          self.model[sReactor]["Thermocouple"] = TemperatureControlModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
          self.model[sReactor]["Stir"] = StirMotorModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
          self.model[sReactor]["Radiation"] = RadiationDetectorModel(sReactor, nReactor, self.hardwareComm, self.modelLock)
      else:
        raise Exception("Unknown system component: " + key)

    # Initialize variables
    self.__pStateMonitor = None
    
  def StartUp(self):
    """Starts the system model"""
    self.stateUpdateThread = StateUpdateThread()
    self.stateUpdateThreadTerminateEvent = threading.Event()
    self.stateUpdateThread.SetParameters(self.hardwareComm, self.stateUpdateThreadTerminateEvent)
    self.stateUpdateThread.start()
        
  def ShutDown(self):
    """Shuts down the system model"""
    self.stateUpdateThreadTerminateEvent.set()
    self.stateUpdateThread.join()
       
  def SetStateMonitor(self, pStateMonitor):
    """Set the state monitor"""
    self.__pStateMonitor = pStateMonitor
       
  def LockSystemModel(self):
    """Acquire the mutex lock and return the system model"""
    self.modelLock.acquire()
    return self.model
    
  def UnlockSystemModel(self):
    """Release the system model lock"""
    self.modelLock.release()

  def ModelUpdated(self):
    """Called when the system model has been updated"""
    if self.__pStateMonitor != None:
        # Catch EOFErrors in the event that the state monitor process dies
        try:
          self.__pStateMonitor.root.UpdateState(self.DumpStateToString())
        except EOFError, ex:
          print "Warning: failed to send state to monitor, will not attempt again"
          self.__pStateMonitor = None
    
  def DumpStateToString(self):
    """Dumps the state to a string"""
    # Acquire a lock on the system model
    self.LockSystemModel()
    sState = ""

    # Perform the state dump in a try/except/finally block to make sure we release our lock on the system model
    try:        
        # Get the robot positions
        nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery = self.model["ReagentDelivery"].getSetPosition(False)
        nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawZ = self.model["ReagentDelivery"].getSetPositionRaw(False)
        nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery = self.model["ReagentDelivery"].getCurrentPosition(False)
        nReagentRobotCurrentPositionRawX, nReagentRobotCurrentPositionRawZ = self.model["ReagentDelivery"].getCurrentPositionRaw(False)
        nReagentRobotCurrentStatusX, nReagentRobotCurrentStatusZ = self.model["ReagentDelivery"].getRobotStatus(False)

        # Format the state into a string
        sState += self.__PadString("Component", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString("Set", STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString("Actual", STATECOMMONCOLUMN2WIDTH)
        sState += "\n"

        sState += self.__PadString("----------------------------------", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString("--------", STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString("--------", STATECOMMONCOLUMN2WIDTH)
        sState += "\n"
        
        # Vacuum system
        sState += self.__PadString("Vacuum system (on/pressure)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["VacuumSystem"].getVacuumSystemOn(False)) + "/" + \
            str(self.model["VacuumSystem"].getVacuumSystemPressure(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"

        # Cooling system
        sState += self.__PadString("Cooling system on", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["CoolingSystem"].getCoolingSystemOn(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"

        # External systems        
        sState += self.__PadString("F-18 valves open (load/elute)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["ExternalSystems"].getF18LoadValveOpen(False)) + "/" + \
            self.__BoolToString(self.model["ExternalSystems"].getF18EluteValveOpen(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"

        sState += self.__PadString("HPLC valve open (load)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["ExternalSystems"].getHPLCLoadValveOpen(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"
        
        # Pressure regulators
        sState += self.__PadString("Pressure regulator 1", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString("%.1f"%(self.model["PressureRegulator1"].getSetPressure(False)), STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString("%.1f"%(self.model["PressureRegulator1"].getCurrentPressure(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("Pressure regulator 2", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString("%.1f"%(self.model["PressureRegulator2"].getSetPressure(False)), STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString("%.1f"%(self.model["PressureRegulator2"].getCurrentPressure(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"
        
        # Reagent robot
        sState += "Reagent robot\n"
        sState += self.__PadString("  Position (reactor/reagent/delivery)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString(str(nReagentRobotSetPositionReactor) + "/" + str(nReagentRobotSetPositionReagent) + "/" + \
            str(nReagentRobotSetPositionDelivery), STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString(str(nReagentRobotCurrentPositionReactor) + "/" + str(nReagentRobotCurrentPositionReagent) + "/" + \
            str(nReagentRobotCurrentPositionDelivery), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("  Raw position (x/z)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString(str(nReagentRobotSetPositionRawX) + "/" + str(nReagentRobotSetPositionRawZ), STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString(str(nReagentRobotCurrentPositionRawX) + "/" + str(nReagentRobotCurrentPositionRawZ), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("  Robot status (x/z)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString("", STATECOMMONCOLUMN2WIDTH)
        sState += self.__PadString(str(nReagentRobotCurrentStatusX) + "/" + str(nReagentRobotCurrentStatusZ), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("  Gripper (up/down)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["ReagentDelivery"].getSetGripperUp(False)) + "/" + \
            self.__BoolToString(self.model["ReagentDelivery"].getSetGripperDown(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n"

        sState += self.__PadString("  Gripper (open/close)", STATECOMMONCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["ReagentDelivery"].getSetGripperOpen(False)) + "/" + \
            self.__BoolToString(self.model["ReagentDelivery"].getSetGripperClose(False)), STATECOMMONCOLUMN2WIDTH)
        sState += "\n\n"
        
        # Reactors
        sState += self.__PadString("Reactor", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString("1", STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString("2", STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString("3", STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("----------------------------", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString("------", STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString("------", STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString("------", STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("Set position", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.model["Reactor1"]["Motion"].getSetPosition(False), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.model["Reactor2"]["Motion"].getSetPosition(False), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.model["Reactor3"]["Motion"].getSetPosition(False), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("Actual position", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.model["Reactor1"]["Motion"].getCurrentPosition(False), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.model["Reactor2"]["Motion"].getCurrentPosition(False), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.model["Reactor3"]["Motion"].getCurrentPosition(False), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("Raw position (set/actual)", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(str(self.model["Reactor1"]["Motion"].getSetPositionRaw(False)) + "/" + \
            str(self.model["Reactor1"]["Motion"].getCurrentPositionRaw(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor2"]["Motion"].getSetPositionRaw(False)) + "/" + \
            str(self.model["Reactor2"]["Motion"].getCurrentPositionRaw(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor3"]["Motion"].getSetPositionRaw(False)) + "/" + \
            str(self.model["Reactor3"]["Motion"].getCurrentPositionRaw(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("Robot status", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(str(self.model["Reactor1"]["Motion"].getCurrentRobotStatus(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor2"]["Motion"].getCurrentRobotStatus(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor3"]["Motion"].getCurrentRobotStatus(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("Reactor up (set/actual)", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor1"]["Motion"].getSetReactorUp(False)) + "/" + \
            self.__BoolToString(self.model["Reactor1"]["Motion"].getCurrentReactorUp(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor2"]["Motion"].getSetReactorUp(False)) + "/" + \
            self.__BoolToString(self.model["Reactor2"]["Motion"].getCurrentReactorUp(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor3"]["Motion"].getSetReactorUp(False)) + "/" + \
            self.__BoolToString(self.model["Reactor3"]["Motion"].getCurrentReactorUp(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("Reactor down (set/actual)", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor1"]["Motion"].getSetReactorDown(False)) + "/" + \
            self.__BoolToString(self.model["Reactor1"]["Motion"].getCurrentReactorDown(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor2"]["Motion"].getSetReactorDown(False)) + "/" + \
            self.__BoolToString(self.model["Reactor2"]["Motion"].getCurrentReactorDown(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor3"]["Motion"].getSetReactorDown(False)) + "/" + \
            self.__BoolToString(self.model["Reactor3"]["Motion"].getCurrentReactorDown(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("Evaporation valves open (N2/vac)", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor1"]["Valves"].getEvaporationNitrogenValveOpen(False)) + \
            "/" + self.__BoolToString(self.model["Reactor1"]["Valves"].getEvaporationVacuumValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor2"]["Valves"].getEvaporationNitrogenValveOpen(False)) + \
            "/" + self.__BoolToString(self.model["Reactor2"]["Valves"].getEvaporationVacuumValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor3"]["Valves"].getEvaporationNitrogenValveOpen(False)) + \
            "/" + self.__BoolToString(self.model["Reactor3"]["Valves"].getEvaporationVacuumValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("Transfer valve open", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor1"]["Valves"].getTransferValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor2"]["Valves"].getTransferValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor3"]["Valves"].getTransferValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("Reagent transfer valves open (1/2)", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor1"]["Valves"].getReagent1TransferValveOpen(False)) + \
            "/" + self.__BoolToString(self.model["Reactor1"]["Valves"].getReagent2TransferValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor2"]["Valves"].getReagent1TransferValveOpen(False)) + \
            "/" + self.__BoolToString(self.model["Reactor2"]["Valves"].getReagent2TransferValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor3"]["Valves"].getReagent1TransferValveOpen(False)) + \
            "/" + self.__BoolToString(self.model["Reactor3"]["Valves"].getReagent2TransferValveOpen(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("Stopcock positions (1/2/3)", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(str(self.model["Reactor1"]["Stopcock1"].getPosition(False)) + "/" + \
            str(self.model["Reactor1"]["Stopcock2"].getPosition(False)) + "/" + str(self.model["Reactor1"]["Stopcock3"].getPosition(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor2"]["Stopcock1"].getPosition(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor3"]["Stopcock1"].getPosition(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("Temp controller (on/set/actual)", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor1"]["Thermocouple"].getHeaterOn(False)) + "/" + \
            str(self.model["Reactor1"]["Thermocouple"].getSetTemperature(False)) + "/" + \
            str(self.model["Reactor1"]["Thermocouple"].getCurrentTemperature(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor2"]["Thermocouple"].getHeaterOn(False)) + "/" + \
            str(self.model["Reactor2"]["Thermocouple"].getSetTemperature(False)) + "/" + \
            str(self.model["Reactor2"]["Thermocouple"].getCurrentTemperature(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(self.__BoolToString(self.model["Reactor3"]["Thermocouple"].getHeaterOn(False)) + "/" + \
            str(self.model["Reactor3"]["Thermocouple"].getSetTemperature(False)) + "/" + \
            str(self.model["Reactor3"]["Thermocouple"].getCurrentTemperature(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
            
        sState += self.__PadString("Stir motor", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(str(self.model["Reactor1"]["Stir"].getCurrentSpeed(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor2"]["Stir"].getCurrentSpeed(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor3"]["Stir"].getCurrentSpeed(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
        
        sState += self.__PadString("Radiation detector", STATEREACTORCOLUMN1WIDTH)
        sState += self.__PadString(str(self.model["Reactor1"]["Radiation"].getRadiation(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor2"]["Radiation"].getRadiation(False)), STATEREACTORCOLUMN2WIDTH)
        sState += self.__PadString(str(self.model["Reactor3"]["Radiation"].getRadiation(False)), STATEREACTORCOLUMN2WIDTH)
        sState += "\n"
    finally:
        # Release the system model lock
        self.UnlockSystemModel()
        
    # Return the state string
    return sState

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
