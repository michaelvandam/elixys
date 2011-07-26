"""System Model

Elixys System Model
"""

# Imports
import time
from threading import Lock
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
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
    # Remember the hardware layer
    self.hardwareComm = hardwareComm
    
    # Create the empty system model and a lock to protect it
    self.model = {}
    self.modelLock = Lock()
    
    # Pass a pointer to the system model so the hardware layer can update our state
    self.hardwareComm.SetSystemModel(self)
  
  def buildSystemModel(self):
    """Create system model from the database"""
    # The system components will ultimately be read from an ini file
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
      
    # Build loop
    for key,value in self.SystemComponents.items():
      if key == "CoolingSystem":
        if value == True:
          # Create the cooling system component
          self.model[key] = CoolingSystemModel(key, self.hardwareComm)
      elif key == "VacuumSystem":
        if value == True:
          # Create the vacuum system component
          self.model[key] = VacuumSystemModel(key, self.hardwareComm)
      elif key == "ExternalSystems":
        if value == True:
          # Create the external systems component
          self.model[key] = ExternalSystemsModel(key, self.hardwareComm)
      elif key == "PressureRegulators":
        for nPressureRegulator in range(1, value + 1):
          # Create a new pressure regulator component
          sPressureRegulator = "PressureRegulator" + str(nPressureRegulator)
          self.model[sPressureRegulator] = PressureRegulatorModel(sPressureRegulator, nPressureRegulator, self.hardwareComm)
      elif key == "ReagentDelivery":
        if value == True:
          # Create the reagent delivery component
          self.model[key] = ReagentDeliveryModel(key, self.hardwareComm)
      elif key == 'Reactors':
        # Create each reactor
        for item in value:
          # Extract the reactor details
          nReactor = item["Reactor"]
          sReactor = "Reactor" + str(nReactor)
          nStopcocks = item["Stopcocks"]
          
          # Create the reactor components
          self.model[sReactor] = {}
          self.model[sReactor]["Motion"] = MotionModel(sReactor, nReactor, self.hardwareComm)
          self.model[sReactor]["Valves"] = ValveModel(sReactor, nReactor, self.hardwareComm)
          for nStopcock in range(1, nStopcocks + 1):
            self.model[sReactor]["Stopcock" + str(nStopcock)] = StopcockValveModel(sReactor, nReactor, nStopcock, self.hardwareComm)
          self.model[sReactor]["Thermocouple"] = TemperatureControlModel(sReactor, nReactor, self.hardwareComm)
          self.model[sReactor]["Stir"] = StirMotorModel(sReactor, nReactor, self.hardwareComm)
          self.model[sReactor]["Radiation"] = RadiationDetectorModel(sReactor, nReactor, self.hardwareComm)
      else:
        raise Exception("Unknown system component: " + key)
        
  def lockSystemModel(self):
    # Acquire the mutex lock and return the system model
    self.modelLock.acquire()
    return self.model
    
  def unlockSystemModel(self):
    # Release the system model lock
    self.modelLock.release()
    
  def DumpStateToString(self):
    """Dumps the state to a string"""
    # Get the robot positions
    nReagentRobotSetPositionReactor, nReagentRobotSetPositionReagent, nReagentRobotSetPositionDelivery = self.model["ReagentDelivery"].getSetPosition()
    nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawZ = self.model["ReagentDelivery"].getSetPositionRaw()
    nReagentRobotCurrentPositionReactor, nReagentRobotCurrentPositionReagent, nReagentRobotCurrentPositionDelivery = self.model["ReagentDelivery"].getCurrentPosition()
    nReagentRobotCurrentPositionRawX, nReagentRobotCurrentPositionRawZ = self.model["ReagentDelivery"].getCurrentPositionRaw()

    # Format the state into a string
    sStateText = "Vacuum system (on/pressure): " + str(self.model["VacuumSystem"].getVacuumSystemOn()) + "/" + str(self.model["VacuumSystem"].getVacuumSystemPressure()) + "\n"
    sStateText += "Cooling system on: " + str(self.model["CoolingSystem"].getCoolingSystemOn()) + "\n"
    sStateText += "External systems:\n"
    sStateText += "  F-18 valves open (load/elute): " + str(self.model["ExternalSystems"].getF18LoadValveOpen()) + "/" + str(self.model["ExternalSystems"].getF18EluteValveOpen()) + "\n"
    sStateText += "  HPLC load valve open: " + str(self.model["ExternalSystems"].getHPLCLoadValveOpen()) + "\n"
    sStateText += "Pressure regulator 1 (set/actual): %.1f/%.1f\n"%(self.model["PressureRegulator1"].getCurrentPressure(), self.model["PressureRegulator1"].getSetPressure())
    sStateText += "Pressure regulator 2 (set/actual): %.1f/%.1f\n"%(self.model["PressureRegulator2"].getCurrentPressure(), self.model["PressureRegulator2"].getSetPressure())
    sStateText += "Reagent robot:\n"
    sStateText += "  Set position (reactor/reagent/delivery): " + str(nReagentRobotSetPositionReactor) + "/" + str(nReagentRobotSetPositionReagent) + "/" + \
        str(nReagentRobotSetPositionDelivery) + "\n"
    sStateText += "  Current position (reactor/reagent/delivery): " + str(nReagentRobotCurrentPositionReactor) + "/" + str(nReagentRobotCurrentPositionReagent) + "/" + \
        str(nReagentRobotCurrentPositionDelivery) + "\n"
    sStateText += "  Set position raw (x/z): " + str(nReagentRobotSetPositionRawX) + "/" + str(nReagentRobotSetPositionRawZ) + "\n"
    sStateText += "  Current position raw (x/z): " + str(nReagentRobotCurrentPositionRawX) + "/" + str(nReagentRobotCurrentPositionRawZ) + "\n"
    sStateText += "  Gripper set (up/down): " + str(self.model["ReagentDelivery"].getSetGripperUp()) + "/" + str(self.model["ReagentDelivery"].getSetGripperDown()) + "\n"
    sStateText += "  Gripper set (open/close): " + str(self.model["ReagentDelivery"].getSetGripperOpen()) + "/" + str(self.model["ReagentDelivery"].getSetGripperClose()) + "\n"
    sStateText += "Reactor 1:\n"
    sStateText += "  Set position (raw): " + self.model["Reactor1"]["Motion"].getSetPosition() + " (" + str(self.model["Reactor1"]["Motion"].getSetPositionRaw()) + ")\n"
    sStateText += "  Current position (raw): " + self.model["Reactor1"]["Motion"].getCurrentPosition() + " (" + str(self.model["Reactor1"]["Motion"].getCurrentPositionRaw()) + ")\n"
    sStateText += "  Reactor up (set/actual): " + str(self.model["Reactor1"]["Motion"].getSetReactorUp()) + "/" + str(self.model["Reactor1"]["Motion"].getCurrentReactorUp()) + "\n"
    sStateText += "  Reactor down (set/actual): " + str(self.model["Reactor1"]["Motion"].getSetReactorDown()) + "/" + str(self.model["Reactor1"]["Motion"].getCurrentReactorDown()) + "\n"
    sStateText += "  Evaporation valves open (nitrogen/vacuum): " + str(self.model["Reactor1"]["Valves"].getEvaporationNitrogenValveOpen()) + "/" + \
        str(self.model["Reactor1"]["Valves"].getEvaporationVacuumValveOpen()) + "\n"
    sStateText += "  Transfer valve open: " + str(self.model["Reactor1"]["Valves"].getTransferValveOpen()) + "\n"
    sStateText += "  Reagent transfer valves open (1/2): " + str(self.model["Reactor1"]["Valves"].getReagent1TransferValveOpen()) + "/" + \
        str(self.model["Reactor1"]["Valves"].getReagent2TransferValveOpen()) + "\n"
    sStateText += "  Stopcock positions (1/2/3): " + str(self.model["Reactor1"]["Stopcock1"].getPosition()) + "/" + str(self.model["Reactor1"]["Stopcock2"].getPosition()) + "/" + \
        str(self.model["Reactor1"]["Stopcock3"].getPosition()) + "\n"
    sStateText += "  Temperature controller (on/set/actual): " + str(self.model["Reactor1"]["Thermocouple"].getHeaterOn()) + "/" + \
        str(self.model["Reactor1"]["Thermocouple"].getSetTemperature()) + "/" + str(self.model["Reactor1"]["Thermocouple"].getCurrentTemperature()) + "\n";
    sStateText += "  Stir motor: " + str(self.model["Reactor1"]["Stir"].getCurrentSpeed()) + "\n"
    sStateText += "  Radiation detector: " + str(self.model["Reactor1"]["Radiation"].getRadiation()) + "\n"
    sStateText += "Reactor 2:\n"
    sStateText += "  Set position (raw): " + self.model["Reactor2"]["Motion"].getSetPosition() + " (" + str(self.model["Reactor2"]["Motion"].getSetPositionRaw()) + ")\n"
    sStateText += "  Current position (raw): " + self.model["Reactor2"]["Motion"].getCurrentPosition() + " (" + str(self.model["Reactor2"]["Motion"].getCurrentPositionRaw()) + ")\n"
    sStateText += "  Reactor up (set/actual): " + str(self.model["Reactor2"]["Motion"].getSetReactorUp()) + "/" + str(self.model["Reactor2"]["Motion"].getCurrentReactorUp()) + "\n"
    sStateText += "  Reactor down (set/actual): " + str(self.model["Reactor2"]["Motion"].getSetReactorDown()) + "/" + str(self.model["Reactor2"]["Motion"].getCurrentReactorDown()) + "\n"
    sStateText += "  Evaporation valves open (nitrogen/vacuum): " + str(self.model["Reactor2"]["Valves"].getEvaporationNitrogenValveOpen()) + "/" + \
        str(self.model["Reactor2"]["Valves"].getEvaporationVacuumValveOpen()) + "\n"
    sStateText += "  Transfer valve open: " + str(self.model["Reactor2"]["Valves"].getTransferValveOpen()) + "\n"
    sStateText += "  Reagent transfer valves open (1/2): " + str(self.model["Reactor2"]["Valves"].getReagent1TransferValveOpen()) + "/" + \
        str(self.model["Reactor2"]["Valves"].getReagent2TransferValveOpen()) + "\n"
    sStateText += "  Stopcock position: " + str(self.model["Reactor2"]["Stopcock1"].getPosition()) + "\n"
    sStateText += "  Temperature controller (on/set/actual): " + str(self.model["Reactor2"]["Thermocouple"].getHeaterOn()) + "/" + \
        str(self.model["Reactor2"]["Thermocouple"].getSetTemperature()) + "/" + str(self.model["Reactor2"]["Thermocouple"].getCurrentTemperature()) + "\n";
    sStateText += "  Stir motor: " + str(self.model["Reactor2"]["Stir"].getCurrentSpeed()) + "\n"
    sStateText += "  Radiation detector: " + str(self.model["Reactor2"]["Radiation"].getRadiation()) + "\n"
    sStateText += "Reactor 3:\n"
    sStateText += "  Set position (raw): " + self.model["Reactor3"]["Motion"].getSetPosition() + " (" + str(self.model["Reactor3"]["Motion"].getSetPositionRaw()) + ")\n"
    sStateText += "  Current position (raw): " + self.model["Reactor3"]["Motion"].getCurrentPosition() + " (" + str(self.model["Reactor3"]["Motion"].getCurrentPositionRaw()) + ")\n"
    sStateText += "  Reactor up (set/actual): " + str(self.model["Reactor3"]["Motion"].getSetReactorUp()) + "/" + str(self.model["Reactor3"]["Motion"].getCurrentReactorUp()) + "\n"
    sStateText += "  Reactor down (set/actual): " + str(self.model["Reactor3"]["Motion"].getSetReactorDown()) + "/" + str(self.model["Reactor3"]["Motion"].getCurrentReactorDown()) + "\n"
    sStateText += "  Evaporation valves open (nitrogen/vacuum): " + str(self.model["Reactor3"]["Valves"].getEvaporationNitrogenValveOpen()) + "/" + \
        str(self.model["Reactor3"]["Valves"].getEvaporationVacuumValveOpen()) + "\n"
    sStateText += "  Transfer valve open: " + str(self.model["Reactor3"]["Valves"].getTransferValveOpen()) + "\n"
    sStateText += "  Reagent transfer valves open (1/2): " + str(self.model["Reactor3"]["Valves"].getReagent1TransferValveOpen()) + "/" + \
        str(self.model["Reactor3"]["Valves"].getReagent2TransferValveOpen()) + "\n"
    sStateText += "  Stopcock position: " + str(self.model["Reactor3"]["Stopcock1"].getPosition()) + "\n"
    sStateText += "  Temperature controller (on/set/actual): " + str(self.model["Reactor3"]["Thermocouple"].getHeaterOn()) + "/" + \
        str(self.model["Reactor3"]["Thermocouple"].getSetTemperature()) + "/" + str(self.model["Reactor3"]["Thermocouple"].getCurrentTemperature()) + "\n";
    sStateText += "  Stir motor: " + str(self.model["Reactor3"]["Stir"].getCurrentSpeed()) + "\n"
    sStateText += "  Radiation detector: " + str(self.model["Reactor3"]["Radiation"].getRadiation()) + "\n"

    # Return the string
    return sStateText

# Test function
if __name__ == "__main__":
  # Create and initialize hardware layer
  pHardwareComm = HardwareComm()
  pHardwareComm.StartUp()
  
  # Create and build the system model
  pSystemModel = SystemModel(pHardwareComm)
  pSystemModel.buildSystemModel()

  # Get the latest state
  pHardwareComm.UpdateState()
  time.sleep(1)
  print pSystemModel.DumpStateToString()
  
  # Clean up
  pHardwareComm.ShutDown()
