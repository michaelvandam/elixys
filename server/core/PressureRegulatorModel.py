"""Pressure Regulator Model

Pressure Regulator Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Pressure regulator model
class PressureRegulatorModel(ComponentModel):
  def __init__(self, name, pressureRegulator, hardwareComm):
    """Pressure regulator model construction"""
    ComponentModel.__init__(self, name, hardwareComm)
    self.pressureRegulator = pressureRegulator
    self.setPressure = 0
    self.currentPressure = 0

  def getMinimumPressure(self):
    """Returns the minimum pressure"""
    return 0
    
  def getMaximumPressure(self):
    """Returns the maximum pressure"""
    return 60
    
  def getSetPressure(self):
    """Returns the set pressure"""
    return self.setPressure
  
  def getCurrentPressure(self):
    """Returns the current pressure"""
    return self.currentPressure
  
  def setPressure(self, nPressure):
    """Sets the set pressure"""
    self.hardwareComm.SetPressureRegulator(self.pressureRegulator, nPressure)

  def updateState(self, nSetPressure, nCurrentPressure):
    """Update the internal state"""
    self.setPressure = nSetPressure
    self.currentPressure = nCurrentPressure