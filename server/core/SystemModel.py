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
        
  def lockSystemModel(self):
    """Acquire the mutex lock and return the system model"""
    self.modelLock.acquire()
    return self.model
    
  def unlockSystemModel(self):
    """Release the system model lock"""
    self.modelLock.release()
    
  def DumpStateToString(self):
    """Dumps the state to a string"""
    # Acquire a lock on the system model
    self.lockSystemModel()
    sState = ""

    # Perform the state dump in a try/except/finally block to make sure we release our lock on the system model
    try:        
        # Get the robot positions
        nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery = self.model["ReagentDelivery"].getSetPosition(False)
        nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawZ = self.model["ReagentDelivery"].getSetPositionRaw(False)
        nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery = self.model["ReagentDelivery"].getCurrentPosition(False)
        nReagentRobotCurrentPositionRawX, nReagentRobotCurrentPositionRawZ = self.model["ReagentDelivery"].getCurrentPositionRaw(False)

        # Format the state into a string
        sState += "Vacuum system (on/pressure): " + str(self.model["VacuumSystem"].getVacuumSystemOn(False)) + "/" + \
            str(self.model["VacuumSystem"].getVacuumSystemPressure(False)) + "\n"
        sState += "Cooling system on: " + str(self.model["CoolingSystem"].getCoolingSystemOn(False)) + "\n"
        sState += "External systems:\n"
        sState += "  F-18 valves open (load/elute): " + str(self.model["ExternalSystems"].getF18LoadValveOpen(False)) + "/" + \
            str(self.model["ExternalSystems"].getF18EluteValveOpen(False)) + "\n"
        sState += "  HPLC load valve open: " + str(self.model["ExternalSystems"].getHPLCLoadValveOpen(False)) + "\n"
        sState += "Pressure regulator 1 (set/actual): %.1f/%.1f\n"%(self.model["PressureRegulator1"].getCurrentPressure(False), \
            self.model["PressureRegulator1"].getSetPressure(False))
        sState += "Pressure regulator 2 (set/actual): %.1f/%.1f\n"%(self.model["PressureRegulator2"].getCurrentPressure(False), \
            self.model["PressureRegulator2"].getSetPressure(False))
        sState += "Reagent robot:\n"
        sState += "  Set position (reactor/reagent/delivery): " + str(nReagentRobotSetPositionReactor) + "/" + \
            str(nReagentRobotSetPositionReagent) + "/" + str(nReagentRobotSetPositionDelivery) + "\n"
        sState += "  Current position (reactor/reagent/delivery): " + str(nReagentRobotCurrentPositionReactor) + "/" + \
            str(nReagentRobotCurrentPositionReagent) + "/" + str(nReagentRobotCurrentPositionDelivery) + "\n"
        sState += "  Set position raw (x/z): " + str(nReagentRobotSetPositionRawX) + "/" + str(nReagentRobotSetPositionRawZ) + "\n"
        sState += "  Current position raw (x/z): " + str(nReagentRobotCurrentPositionRawX) + "/" + str(nReagentRobotCurrentPositionRawZ) + "\n"
        sState += "  Gripper set (up/down): " + str(self.model["ReagentDelivery"].getSetGripperUp(False)) + "/" + \
            str(self.model["ReagentDelivery"].getSetGripperDown(False)) + "\n"
        sState += "  Gripper set (open/close): " + str(self.model["ReagentDelivery"].getSetGripperOpen(False)) + "/" + \
            str(self.model["ReagentDelivery"].getSetGripperClose(False)) + "\n"
        sState += "Reactor 1:\n"
        sState += "  Set position (raw): " + self.model["Reactor1"]["Motion"].getSetPosition(False) + " (" + \
            str(self.model["Reactor1"]["Motion"].getSetPositionRaw(False)) + ")\n"
        sState += "  Current position (raw): " + self.model["Reactor1"]["Motion"].getCurrentPosition(False) + " (" + \
            str(self.model["Reactor1"]["Motion"].getCurrentPositionRaw(False)) + ")\n"
        sState += "  Reactor up (set/actual): " + str(self.model["Reactor1"]["Motion"].getSetReactorUp(False)) + "/" + \
            str(self.model["Reactor1"]["Motion"].getCurrentReactorUp(False)) + "\n"
        sState += "  Reactor down (set/actual): " + str(self.model["Reactor1"]["Motion"].getSetReactorDown(False)) + "/" + \
            str(self.model["Reactor1"]["Motion"].getCurrentReactorDown(False)) + "\n"
        sState += "  Evaporation valves open (nitrogen/vacuum): " + str(self.model["Reactor1"]["Valves"].getEvaporationNitrogenValveOpen(False)) + \
            "/" + str(self.model["Reactor1"]["Valves"].getEvaporationVacuumValveOpen(False)) + "\n"
        sState += "  Transfer valve open: " + str(self.model["Reactor1"]["Valves"].getTransferValveOpen(False)) + "\n"
        sState += "  Reagent transfer valves open (1/2): " + str(self.model["Reactor1"]["Valves"].getReagent1TransferValveOpen(False)) + \
            "/" + str(self.model["Reactor1"]["Valves"].getReagent2TransferValveOpen(False)) + "\n"
        sState += "  Stopcock positions (1/2/3): " + str(self.model["Reactor1"]["Stopcock1"].getPosition(False)) + "/" + \
            str(self.model["Reactor1"]["Stopcock2"].getPosition(False)) + "/" + str(self.model["Reactor1"]["Stopcock3"].getPosition(False)) + "\n"
        sState += "  Temperature controller (on/set/actual): " + str(self.model["Reactor1"]["Thermocouple"].getHeaterOn(False)) + "/" + \
            str(self.model["Reactor1"]["Thermocouple"].getSetTemperature(False)) + "/" + \
            str(self.model["Reactor1"]["Thermocouple"].getCurrentTemperature(False)) + "\n";
        sState += "  Stir motor: " + str(self.model["Reactor1"]["Stir"].getCurrentSpeed(False)) + "\n"
        sState += "  Radiation detector: " + str(self.model["Reactor1"]["Radiation"].getRadiation(False)) + "\n"
        sState += "Reactor 2:\n"
        sState += "  Set position (raw): " + self.model["Reactor2"]["Motion"].getSetPosition(False) + " (" + \
            str(self.model["Reactor2"]["Motion"].getSetPositionRaw(False)) + ")\n"
        sState += "  Current position (raw): " + self.model["Reactor2"]["Motion"].getCurrentPosition(False) + " (" + \
            str(self.model["Reactor2"]["Motion"].getCurrentPositionRaw(False)) + ")\n"
        sState += "  Reactor up (set/actual): " + str(self.model["Reactor2"]["Motion"].getSetReactorUp(False)) + "/" + \
            str(self.model["Reactor2"]["Motion"].getCurrentReactorUp(False)) + "\n"
        sState += "  Reactor down (set/actual): " + str(self.model["Reactor2"]["Motion"].getSetReactorDown(False)) + "/" + \
            str(self.model["Reactor2"]["Motion"].getCurrentReactorDown(False)) + "\n"
        sState += "  Evaporation valves open (nitrogen/vacuum): " + str(self.model["Reactor2"]["Valves"].getEvaporationNitrogenValveOpen(False)) + \
            "/" + str(self.model["Reactor2"]["Valves"].getEvaporationVacuumValveOpen(False)) + "\n"
        sState += "  Transfer valve open: " + str(self.model["Reactor2"]["Valves"].getTransferValveOpen(False)) + "\n"
        sState += "  Reagent transfer valves open (1/2): " + str(self.model["Reactor2"]["Valves"].getReagent1TransferValveOpen(False)) + \
            "/" + str(self.model["Reactor2"]["Valves"].getReagent2TransferValveOpen(False)) + "\n"
        sState += "  Stopcock position: " + str(self.model["Reactor2"]["Stopcock1"].getPosition(False)) + "\n"
        sState += "  Temperature controller (on/set/actual): " + str(self.model["Reactor2"]["Thermocouple"].getHeaterOn(False)) + "/" + \
            str(self.model["Reactor2"]["Thermocouple"].getSetTemperature(False)) + "/" + \
            str(self.model["Reactor2"]["Thermocouple"].getCurrentTemperature(False)) + "\n";
        sState += "  Stir motor: " + str(self.model["Reactor2"]["Stir"].getCurrentSpeed(False)) + "\n"
        sState += "  Radiation detector: " + str(self.model["Reactor2"]["Radiation"].getRadiation(False)) + "\n"
        sState += "Reactor 3:\n"
        sState += "  Set position (raw): " + self.model["Reactor3"]["Motion"].getSetPosition(False) + " (" + \
            str(self.model["Reactor3"]["Motion"].getSetPositionRaw(False)) + ")\n"
        sState += "  Current position (raw): " + self.model["Reactor3"]["Motion"].getCurrentPosition(False) + " (" + \
            str(self.model["Reactor3"]["Motion"].getCurrentPositionRaw(False)) + ")\n"
        sState += "  Reactor up (set/actual): " + str(self.model["Reactor3"]["Motion"].getSetReactorUp(False)) + "/" + \
            str(self.model["Reactor3"]["Motion"].getCurrentReactorUp(False)) + "\n"
        sState += "  Reactor down (set/actual): " + str(self.model["Reactor3"]["Motion"].getSetReactorDown(False)) + "/" + \
            str(self.model["Reactor3"]["Motion"].getCurrentReactorDown(False)) + "\n"
        sState += "  Evaporation valves open (nitrogen/vacuum): " + str(self.model["Reactor3"]["Valves"].getEvaporationNitrogenValveOpen(False)) + \
            "/" + str(self.model["Reactor3"]["Valves"].getEvaporationVacuumValveOpen(False)) + "\n"
        sState += "  Transfer valve open: " + str(self.model["Reactor3"]["Valves"].getTransferValveOpen(False)) + "\n"
        sState += "  Reagent transfer valves open (1/2): " + str(self.model["Reactor3"]["Valves"].getReagent1TransferValveOpen(False)) + "/" + \
            str(self.model["Reactor3"]["Valves"].getReagent2TransferValveOpen(False)) + "\n"
        sState += "  Stopcock position: " + str(self.model["Reactor3"]["Stopcock1"].getPosition(False)) + "\n"
        sState += "  Temperature controller (on/set/actual): " + str(self.model["Reactor3"]["Thermocouple"].getHeaterOn(False)) + "/" + \
            str(self.model["Reactor3"]["Thermocouple"].getSetTemperature(False)) + "/" + \
            str(self.model["Reactor3"]["Thermocouple"].getCurrentTemperature(False)) + "\n";
        sState += "  Stir motor: " + str(self.model["Reactor3"]["Stir"].getCurrentSpeed(False)) + "\n"
        sState += "  Radiation detector: " + str(self.model["Reactor3"]["Radiation"].getRadiation(False)) + "\n"
    finally:
        # Release the system model lock
        self.unlockSystemModel()

    # Return the state string
    return sState
